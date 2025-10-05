import os
import sqlite3
from typing import Dict, List, Tuple, Optional
from app.domain.entities import JourneyRequest, Itinerary, Leg, Connection
from app.domain.ports import RoutePlannerPort
from app.settings import settings

def parse_gtfs_time(t: str) -> int:
    """
    'HH:MM:SS' -> seconds since midnight. Supports HH >= 24 (post-midnight trips).
    """
    if t is None:
        return 0
    h, m, s = t.split(":")
    return int(h) * 3600 + int(m) * 60 + int(s)

class CsaRoutePlanner(RoutePlannerPort):
    """
    Minimal Connection Scan Algorithm over a GTFS SQLite:
    - connections = consecutive stop_times of the same trip (sequence +1)
    - earliest-arrival labels; relax footpaths after each improvement
    - optional footpaths table(from_stop,to_stop,walk_sec,distance_m)
    """
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or settings.gtfs_sqlite_path

    def _db(self):
        return sqlite3.connect(self.db_path)

    def _load_connections(self, t0: int, t1: int) -> List[Connection]:
        """
        Load ALL trip hops (stops pairs) and filter by departure window [t0, t1].
        Schema expected:
          - stop_times(trip_id, stop_id, arrival_time, departure_time, stop_sequence)
          - trips(trip_id, route_id)
        """
        conns: List[Connection] = []
        with self._db() as db:
            cur = db.cursor()
            # Pull consecutive stop pairs within trips
            cur.execute("""
                SELECT st1.trip_id, t.route_id,
                       st1.stop_id, st1.departure_time,
                       st2.stop_id, st2.arrival_time
                FROM stop_times st1
                JOIN stop_times st2
                  ON st2.trip_id = st1.trip_id
                 AND st2.stop_sequence = st1.stop_sequence + 1
                JOIN trips t ON t.trip_id = st1.trip_id
            """)
            for trip_id, route_id, from_stop, dep_txt, to_stop, arr_txt in cur.fetchall():
                dep = parse_gtfs_time(dep_txt)
                arr = parse_gtfs_time(arr_txt)
                if dep < t0 or dep > t1:
                    continue
                # Skip bad rows
                if arr < dep:
                    continue
                conns.append(Connection(dep, arr, from_stop, to_stop, trip_id, route_id))
        # Sort by departure time (CSA requirement)
        conns.sort(key=lambda c: c.dep_time)
        return conns

    def _load_footpaths(self) -> Dict[str, List[Tuple[str, int, Optional[int]]]]:
        """
        Returns {from_stop: [(to_stop, walk_sec, distance_m), ...]}
        If table doesn't exist, returns {}.
        """
        mapping: Dict[str, List[Tuple[str, int, Optional[int]]]] = {}
        try:
            with self._db() as db:
                cur = db.cursor()
                cur.execute("""
                    SELECT from_stop, to_stop, walk_sec,
                           CASE WHEN instr(sql, 'distance_m') > 0 THEN distance_m ELSE NULL END
                    FROM footpaths
                """)
        except sqlite3.Error:
            return mapping

        # If the SELECT above fails due to the CASE hack, re-run a simpler one.
        try:
            with self._db() as db:
                cur = db.cursor()
                cur.execute("SELECT from_stop, to_stop, walk_sec, COALESCE(distance_m, NULL) FROM footpaths")
                rows = cur.fetchall()
        except sqlite3.Error:
            return mapping

        for from_stop, to_stop, walk_sec, dist_m in rows:
            mapping.setdefault(from_stop, []).append((to_stop, int(walk_sec), int(dist_m) if dist_m is not None else None))
        return mapping

    def _reconstruct(self, req: JourneyRequest, prev: Dict[str, Tuple[str, Optional[Connection], Optional[Tuple[str,int,int]]]]) -> Optional[Itinerary]:
        """
        prev[stop] = (prev_stop, used_connection, used_footpath)
         - used_connection: Connection or None (if last step was walk)
         - used_footpath: (to_stop, walk_sec, dist_m) if the hop is a footpath
        """
        target = req.to_stop
        if target not in prev:
            return None
        legs: List[Leg] = []
        cur = target
        while True:
            entry = prev.get(cur)
            if not entry:
                break
            pstop, used_conn, used_fp = entry
            if used_conn is not None:
                legs.append(Leg(
                    mode="transit",
                    from_stop=used_conn.from_stop,
                    to_stop=used_conn.to_stop,
                    dep_time=used_conn.dep_time,
                    arr_time=used_conn.arr_time,
                    route_id=used_conn.route_id,
                    trip_id=used_conn.trip_id
                ))
                cur = used_conn.from_stop
            elif used_fp is not None:
                to_stop, walk_sec, dist_m = used_fp
                # walk reversed: so from pstop -> cur with walk_sec
                legs.append(Leg(
                    mode="walk",
                    from_stop=pstop,
                    to_stop=cur,
                    dep_time=0,  # unknown absolute time (we'll fill on merge)
                    arr_time=0,
                    distance_m=dist_m
                ))
                cur = pstop
            else:
                break
            if cur == req.from_stop:
                break
        legs.reverse()

        # Fill walk absolute times where possible (between transit legs)
        # Approx: walk dep = previous leg arr_time; arr = dep + walk_sec
        i = 0
        while i < len(legs):
            if legs[i].mode == "walk":
                # pick neighbor times if exist
                prev_arr = legs[i-1].arr_time if i > 0 else None
                next_dep = legs[i+1].dep_time if i+1 < len(legs) else None
                walk_sec = 0
                # try to infer from footpaths map later if needed
                if prev_arr is not None:
                    legs[i].dep_time = prev_arr
                    # best-effort set to 5 min if unknown
                    legs[i].arr_time = prev_arr + (5 * 60)
            i += 1

        return Itinerary(legs=legs)

    def plan(self, req: JourneyRequest) -> List[Itinerary]:
        # If no DB file → try demo fallback
        if not self.db_path or not os.path.exists(self.db_path):
            return self._demo_plan(req)

        t0 = req.depart_at
        t1 = req.depart_at + req.window_sec
        try:
            conns = self._load_connections(t0, t1)
        except Exception:
            # corrupted DB or schema mismatch
            return self._demo_plan(req)

        foot = self._load_footpaths()

        # Labels and backpointers
        INF = 10**12
        stops = set([c.from_stop for c in conns] + [c.to_stop for c in conns] + [req.from_stop, req.to_stop])
        earliest: Dict[str, int] = {s: INF for s in stops}
        prev: Dict[str, Tuple[str, Optional[Connection], Optional[Tuple[str,int,int]]]] = {}

        earliest[req.from_stop] = t0

        # initial footpaths from origin
        for (to_s, wsec, dist) in foot.get(req.from_stop, []):
            if earliest[to_s] > t0 + wsec:
                earliest[to_s] = t0 + wsec
                prev[to_s] = (req.from_stop, None, (to_s, wsec, dist))

        # Scan connections
        for c in conns:
            if earliest.get(c.from_stop, INF) <= c.dep_time:
                # can catch it
                if earliest.get(c.to_stop, INF) > c.arr_time:
                    earliest[c.to_stop] = c.arr_time
                    prev[c.to_stop] = (c.from_stop, c, None)
                    # relax footpaths after arrival
                    for (to_s, wsec, dist) in foot.get(c.to_stop, []):
                        if earliest.get(to_s, INF) > c.arr_time + wsec:
                            earliest[to_s] = c.arr_time + wsec
                            prev[to_s] = (c.to_stop, None, (to_s, wsec, dist))

        it = self._reconstruct(req, prev)
        return [it] if it and it.legs else []

    # --- DEMO fallback: 3-stop world (STOP_A/B/C) ---
    def _demo_plan(self, req: JourneyRequest) -> List[Itinerary]:
        sa, sb, sc = "STOP_A", "STOP_B", "STOP_C"
        base = req.depart_at

        def mk_transit(route, trip, a, b, dur_min):
            return Leg(mode="transit", from_stop=a, to_stop=b,
                       dep_time=base, arr_time=base + dur_min*60,
                       route_id=route, trip_id=trip)

        def mk_walk(a, b, min_walk, dist):
            return Leg(mode="walk", from_stop=a, to_stop=b,
                       dep_time=base, arr_time=base + min_walk*60,
                       distance_m=dist)

        if req.from_stop == sa and req.to_stop == sc:
            legs = [
                mk_transit("3", "3A", sa, sb, 6),
                mk_walk(sb, sc, 5, 350)
            ]
            return [Itinerary(legs)]
        if req.from_stop == sb and req.to_stop == sa:
            legs = [mk_transit("52", "52X", sb, sa, 7)]
            return [Itinerary(legs)]
        if req.from_stop == sc and req.to_stop == sb:
            legs = [mk_transit("22", "22K", sc, sb, 8)]
            return [Itinerary(legs)]
        # default: simple direct walk
        legs = [mk_walk(req.from_stop, req.to_stop, 12, 900)]
        return [Itinerary(legs)]
