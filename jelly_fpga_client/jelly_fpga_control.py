

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

    def open_uio(self, name, unit=0):
        response = self.stub.OpenUio(jelly_fpga_control_pb2.OpenUioRequest(name=name, unit=unit))
        if not response.result:
            return None
        return response.id

    def open_udmabuf(self, name, cache_enable=False, unit=0):
        response = self.stub.OpenUdmabuf(jelly_fpga_control_pb2.OpenUdmabufRequest(name=name, cache_enable=cache_enable, unit=unit))
        if not response.result:
            return None
        return response.id

    def subclone(self, id, offset, size, unit=0):
        response = self.stub.Subclone(jelly_fpga_control_pb2.SubcloneRequest(id=id, offset=offset, size=size, unit=unit))
        if not response.result:
            return None
        return response.id

    def get_addr(self, id):
        response = self.stub.GetAddr(jelly_fpga_control_pb2.GetAddrRequest(id=id))
        if not response.result:
            return None
        return response.addr

    def get_size(self, id):
        response = self.stub.GetSize(jelly_fpga_control_pb2.GetSizeRequest(id=id))
        if not response.result:
            return None
        return response.size

    def get_phys_addr(self, id):
        response = self.stub.GetPhysAddr(jelly_fpga_control_pb2.GetPhysAddrRequest(id=id))
        if not response.result:
            return None
        return response.phys_addr

    def close(self, id):
        response = self.stub.Close(jelly_fpga_control_pb2.CloseRequest(id=id))
        return response.result

    def write_mem_u(self, id, offset, data, size=0):
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

    def write_mem_i(self, id, offset, data, size=0):
        response = self.stub.WriteMemI(jelly_fpga_control_pb2.WriteMemIRequest(id=id, offset=offset, data=data, size=size))
        return response.result

    def write_mem_i8(self, id, offset, data):
        return self.write_mem_i(id, offset, data, 1)

    def write_mem_i16(self, id, offset, data):
        return self.write_mem_i(id, offset, data, 2)

    def write_mem_i32(self, id, offset, data):
        return self.write_mem_i(id, offset, data, 4)

    def write_mem_i64(self, id, offset, data):
        return self.write_mem_i(id, offset, data, 8)

    def read_mem_u(self, id, offset, size=0):
        response = self.stub.ReadMemU(jelly_fpga_control_pb2.ReadMemRequest(id=id, offset=offset, size=size))
        if not response.result:
            return None
        return response.data
    
    def read_mem_u8(self, id, offset):
        return self.read_mem_u(id, offset, 1)
    
    def read_mem_u16(self, id, offset):
        return self.read_mem_u(id, offset, 2)
    
    def read_mem_u32(self, id, offset):
        return self.read_mem_u(id, offset, 4)
    
    def read_mem_u64(self, id, offset):
        return self.read_mem_u(id, offset, 8)
    
    def read_mem_i(self, id, offset, size=0):
        response = self.stub.ReadMemI(jelly_fpga_control_pb2.ReadMemRequest(id=id, offset=offset, size=size))
        if not response.result:
            return None
        return response.data
    
    def read_mem_i8(self, id, offset):
        return self.read_mem_i(id, offset, 1)
    
    def read_mem_i16(self, id, offset):
        return self.read_mem_i(id, offset, 2)
    
    def read_mem_i32(self, id, offset):
        return self.read_mem_i(id, offset, 4)
    
    def read_mem_i64(self, id, offset):
        return self.read_mem_i(id, offset, 8)
    
    def write_reg_u(self, id, reg, data, size=0):
        response = self.stub.WriteRegU(jelly_fpga_control_pb2.WriteRegURequest(id=id, reg=reg, data=data, size=size))
        return response.result
    
    def write_reg_u8(self, id, reg, data):
        return self.write_reg_u(id, reg, data, 1)
    
    def write_reg_u16(self, id, reg, data):
        return self.write_reg_u(id, reg, data, 2)
    
    def write_reg_u32(self, id, reg, data):
        return self.write_reg_u(id, reg, data, 4)
    
    def write_reg_u64(self, id, reg, data):
        return self.write_reg_u(id, reg, data, 8)
    
    def write_reg_i(self, id, reg, data, size=0):
        response = self.stub.WriteRegI(jelly_fpga_control_pb2.WriteRegIRequest(id=id, reg=reg, data=data, size=size))
        return response.result
    
    def write_reg_i8(self, id, reg, data):
        return self.write_reg_i(id, reg, data, 1)
    
    def write_reg_i16(self, id, reg, data):
        return self.write_reg_i(id, reg, data, 2)
    
    def write_reg_i32(self, id, reg, data):
        return self.write_reg_i(id, reg, data, 4)
    
    def write_reg_i64(self, id, reg, data):
        return self.write_reg_i(id, reg, data, 8)

    def read_reg_u(self, id, reg, size=0):
        response = self.stub.ReadRegU(jelly_fpga_control_pb2.ReadRegRequest(id=id, reg=reg, size=size))
        if not response.result:
            return None
        return response.data
    
    def read_reg_u8(self, id, reg):
        return self.read_reg_u(id, reg, 1)
    
    def read_reg_u16(self, id, reg):
        return self.read_reg_u(id, reg, 2)
    
    def read_reg_u32(self, id, reg):
        return self.read_reg_u(id, reg, 4)
    
    def read_reg_u64(self, id, reg):
        return self.read_reg_u(id, reg, 8)
    
    def read_reg_i(self, id, reg, size=0):
        response = self.stub.ReadRegI(jelly_fpga_control_pb2.ReadRegRequest(id=id, reg=reg, size=size))
        if not response.result:
            return None
        return response.data
    
    def read_reg_i8(self, id, reg):
        return self.read_reg_i(id, reg, 1)
    
    def read_reg_i16(self, id, reg):
        return self.read_reg_i(id, reg, 2)
    
    def read_reg_i32(self, id, reg):
        return self.read_reg_i(id, reg, 4)
    
    def read_reg_i64(self, id, reg):
        return self.read_reg_i(id, reg, 8)
