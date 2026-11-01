from dns_checker import check_dns
from tcp_checker import check_tcp

domain = input("Enter domain: ").strip()

if domain == "":
    print(f"[ERROR] Domain cannot be empty")
else:
    ip = check_dns(domain)

    if ip is not None:
        print(f"[PASS] IP: {ip}")
    else:
        print(f"[FAIL] DNS Resolution Failed")
    
    


