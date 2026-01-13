from __future__ import annotations

import socket
from typing import Optional


def resolve(host: str) -> tuple[list[str], Optional[str]]:
    """
    도메인 이름을 IP 주소 리스트로 변환합니다.
    """
    try:
        # socket.getaddrinfo의 반환값 = (family, type, proto, canonname, sockaddr)
        # infos (리스트) : [[0], [1], [2], [3], [4]], [[0], [1], [2], [3],[4] ...] 의 구조
        infos = socket.getaddrinfo(host, None, proto=socket.IPPROTO_TCP)
        
        ###########################################################
        ips: list[str] = [] 
        # [0] = family, [1] = type, [2] = proto, [3] = cannoname, [4] = sockaddr
        # sockaddr = [ip 주소, port] -> sockaddr[0]만 추출
        for i in infos :
            sockaddr = i[4]
            ip = str(sockaddr[0])

            if ip not in ips : # 중복 제거
                ips.append(ip)

        ###########################################################

        return ips, None
    except Exception as e:
        return [], str(e)


def pick_ip(ips: list[str], prefer: str = "any") -> Optional[str]:
    """
    주어진 IP 리스트 중 prefer 정책에 맞는 최적의 IP 하나를 선택하여 반환합니다. 
    
    요구사항:
    1. prefer가 "ipv4"인 경우: 리스트에서 가장 먼저 발견되는 IPv4 주소(:가 없는 주소)를 반환합니다. 
    2. prefer가 "ipv6"인 경우: 리스트에서 가장 먼저 발견되는 IPv6 주소(:가 있는 주소)를 반환합니다. 
    3. 정책에 맞는 주소가 없거나 prefer가 "any"인 경우: 리스트의 첫 번째 주소를 반환합니다. 
    """
    if not ips:
        return None

    ###########################################################
    # 1. prefer가 "ipv4"인 경우: 리스트에서 가장 먼저 발견되는 IPv4 주소(:가 없는 주소)를 반환 
    if prefer.lower() == "ipv4" :
        for ip in ips :
            if ":" not in ip :
                return ip
    
    # 2. prefer가 "ipv6"인 경우: 리스트에서 가장 먼저 발견되는 IPv6 주소(:가 있는 주소)를 반환
    if prefer.lower() == "ipv6" :
        for ip in ips :
            if ":" in ip :
                return ip
    
    ###########################################################

    # 3. 정책에 맞는 주소가 없거나 prefer가 "any"인 경우: 리스트의 첫 번째 주소를 반환
    return ips[0]