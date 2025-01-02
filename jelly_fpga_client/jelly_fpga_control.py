

import os
import sys
import grpc


sys.path.append(os.path.dirname(__file__))

from jelly_fpga_client import jelly_fpga_control_pb2
from jelly_fpga_client import jelly_fpga_control_pb2_grpc

class JellyFpgaControl:
    def __init__(self, target="localhost:50051"):
        self.channel = grpc.insecure_channel(target)
        self.stub = jelly_fpga_control_pb2_grpc.JellyFpgaControlStub(self.channel)

    def reset(self):
        response = self.stub.Reset(jelly_fpga_control_pb2.ResetRequest())
        return response.result

    def load(self, name):
        response = self.stub.Load(jelly_fpga_control_pb2.LoadRequest(name=name))
        return response.result

    def unload(self, slot=0):
        response = self.stub.Unload(jelly_fpga_control_pb2.UnloadRequest(slot=slot))
        return response.result

    def upload_firmware(self, name, data, chunk_size=2*1024*1024):
        def generate_message(name, data):
            while len(data) > 0:
                yield jelly_fpga_control_pb2.UploadFirmwareRequest(name=name, data=data[:chunk_size])
                data = data[chunk_size:]
        response = self.stub.UploadFirmware(generate_message(name, data))
        return response.result

    def upload_firmware_file(self, name, path, chunk_size=2*1024*1024):
        with open(path, "rb") as f:
            self.upload_firmware(name, f.read(), chunk_size)

    def remove_firmware(self, name):
        response = self.stub.RemoveFirmware(jelly_fpga_control_pb2.RemoveFirmwareRequest(name=name))
        return response.result

    def dts_to_dtb(self, dts):
        response = self.stub.DtsToDtb(jelly_fpga_control_pb2.DtsToDtbRequest(dts=dts))
        if not response.result:
            return None
        return response.dtb
    
    def bitstream_to_bin(self, bitstream_name, bin_name, arch):
        response = self.stub.BitstreamToBin(jelly_fpga_control_pb2.BitstreamToBinRequest(bitstream_name=bitstream_name, bin_name=bin_name, arch=arch))
        return response.result

    def load_dtbo(self, name):
        response = self.stub.LoadDtbo(jelly_fpga_control_pb2.LoadDtboRequest(name=name))
        return response.result

    def load_bin(self, name):
        response = self.stub.LoadBitstream(jelly_fpga_control_pb2.LoadBitstreamRequest(name=name))
        return response.result

    def load_bitstream(self, name):
        response = self.stub.LoadBitstream(jelly_fpga_control_pb2.LoadBitstreamRequest(name=name))
        return response.result

    def open_mmap(self, path, offset, size, unit=0):
        response = self.stub.OpenMmap(jelly_fpga_control_pb2.OpenMmapRequest(path=path, offset=offset, size=size, unit=unit))
        if not response.result:
            return None
        return response.id
    
    def close(self, id):
        response = self.stub.Close(jelly_fpga_control_pb2.CloseRequest(id=id))
        return response.result

    def write_mem_u(self, id, offset, data, size):
        response = self.stub.WriteMemU(jelly_fpga_control_pb2.WriteMemURequest(id=id, offset=offset, data=data, size=size))
        return response.result

    def write_mem_u8(self, id, offset, data):
        return self.write_mem_u(id, offset, data, 1)

    def write_mem_u16(self, id, offset, data):
        return self.write_mem_u(id, offset, data, 2)

    def write_mem_u32(self, id, offset, data):
        return self.write_mem_u(id, offset, data, 4)

    def write_mem_u64(self, id, offset, data):
        return self.write_mem_u(id, offset, data, 8)
