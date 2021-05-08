from r2a.ir2a import IR2A
from player.parser import *
import time
import bisect

class R2ANewAlgorithm(IR2A):

    def __init__(self, id):
        IR2A.__init__(self, id)
        self.throughput = 0
        self.time_request = 0
        self.time_response = 0

    def handle_xml_request(self, msg):
        self.time_request = time.perf_counter()
        self.send_down(msg)

    def handle_xml_response(self, msg):
        parsed_mpd = parse_mpd(msg.get_payload())
        self.qi = parsed_mpd.get_qi()

        self.time_response = time.perf_counter()
        self.throughput = msg.get_bit_length()/(self.time_response - self.time_request)
        self.send_up(msg)

    def handle_segment_size_request(self, msg):
        selected_qi = self.qi[max(0, bisect.bisect_left(self.qi, (self.throughput/2)) - 1)]
        msg.add_quality_id(selected_qi)

        self.time_request = time.perf_counter()
        self.send_down(msg)

    def handle_segment_size_response(self, msg):
        self.time_response = time.perf_counter()
        # valor calculado com base no algoritmo proposto no artigo A seamless Web integration of adaptive HTTP streaming
        self.throughput = 0.65 * (msg.get_bit_length()/(self.time_response - self.time_request)) + 0.35 * self.throughput

        self.send_up(msg)

    def initialize(self):
        IR2A.initialize(self)
        pass

    def finalization(self):
        IR2A.finalization(self)
        pass