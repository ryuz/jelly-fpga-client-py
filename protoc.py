#!/usr/bin/env python3

from grpc.tools import protoc

protoc.main(
    (
        '',
        '-I./jelly-fpga-server/protos',
        '--python_out=./jelly_fpga_client',
        '--grpc_python_out=./jelly_fpga_client',
        'jelly_fpga_control.proto'
    )
)
