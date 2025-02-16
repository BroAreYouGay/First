import socket
import os
import time
import threading
from colorama import Fore, Style

port_services = {
    21: "FTP",
    22: "SSH",
    23: "Telnet",
    25: "SMTP",
    53: "DNS",
    80: "HTTP",
    110: "POP3",
    143: "IMAP",
    443: "HTTPS",
    3306: "MySQL",
    3389: "RDP"
}

thread_limit = threading.Semaphore(100)

def scanOnePort(ip, port, allResultsOptions=False):
    with thread_limit:
        try:
            sockTCP = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sockTCP.settimeout(1)
            result = sockTCP.connect_ex((ip, port))
            
            if result == 0:
                service = port_services.get(port, socket.getservbyport(port, "tcp") if port in range(1, 65536) else "Unknown Service")
                print(f"[+] {ip}:{port}: OPEN ({service})")
            elif allResultsOptions:
                print(f"[-] {ip}:{port}: CLOSED")
        except socket.error as e:
            print(f"Erreur lors du scan du port {port} sur {ip}: {e}")
        finally:
            sockTCP.close()

def scanMultiplePorts(ip, port_S, port_E):
    threads = []
    for port in range(port_S, port_E + 1):
        thread = threading.Thread(target=scanOnePort, args=(ip, port))
        threads.append(thread)
        thread.start()
    for thread in threads:
        thread.join()
    print("Scan complete.")

def is_ip_online(ip, ports=[22, 80, 443, 3389, 53]):
    for port in ports:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.5)
        result = sock.connect_ex((ip, port))
        sock.close()
        if result == 0:
            print(f"{ip} is ONLINE")
            return True
    print(f"{ip} is OFFLINE or well-firewalled (no open ports detected).")
    return False

def is_valid_ip(ip):
    parts = ip.split('.')
    return len(parts) == 4 and all(part.isdigit() and 0 <= int(part) <= 255 for part in parts)

def get_ip():
    while True:
        ip = input("Please enter an IP address (x.x.x.x) or 'x' to return to menu: ")
        if ip.lower() == "x":
            return None
        if is_valid_ip(ip) and is_ip_online(ip):
            return ip
        print("Invalid IP... please enter a valid IP address or CTRL+C to leave.")

def is_valid_port(port):
    return port.isdigit() and 1 <= int(port) <= 65535

def get_port_and_scan(ip):
    while True:
        port = input(f"Ok enter the port for {ip} (or 'x' to return to menu): ").strip()
        if port.lower() == "x":
            return
        if is_valid_port(port):
            scanOnePort(ip, int(port), allResultsOptions=True)
            time.sleep(3)
            return
        print("Invalid port. Please enter a number between 1 and 65535.")

def get_ports_and_scan(ip):
    while True:
        ports_input = input(f"Enter ports to scan for {ip} (ex: 22,80,443 or 20-100) or 'x' to return: ").replace(" ", "")
        if ports_input.lower() == "x":
            return 
        if "-" in ports_input:
            try:
                start, end = map(int, ports_input.split("-"))
                if 1 <= start <= 65535 and 1 <= end <= 65535 and start < end:
                    scanMultiplePorts(ip, start, end)
                    time.sleep(3)
                    return 
            except ValueError:
                pass
        elif "," in ports_input:
            try:
                ports = list(map(int, ports_input.split(",")))
                if all(1 <= port <= 65535 for port in ports):
                    for port in ports:
                        scanOnePort(ip, port, allResultsOptions=True)
                        time.sleep(3)
                    return
            except ValueError:
                pass
        print("Invalid input. Use format: 22,80,443 or 20-100.")

def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

def banner():
    print("""
                (          (                     
                )\ )       )\ )                  
                (()/( (    (()/(         )        
                /(_)))\ )  /(_)) (   ( /(   (    
                (_)) (()/( (_))   )\  )(_))  )\ ) 
                | _ \ )(_))/ __| ((_)((_)_  _(_/( 
                |  _/| || |\__ \/ _| / _` || ' \))
                |_|   \_, ||___/\__| \__,_||_||_| 
                    |__/
          """)

def port_usage_information():
    clear_console()
    print("\n=== Port Usage Information ===")
    for port, service in port_services.items():
        print(f"Port {port}: {service}")
    print("\nPort Ranges:")
    print("1-1023: Well-known ports (used by core services like HTTP, SSH, FTP, etc.)")
    print("1024-49151: Registered ports (used by software applications)")
    print("49152-65535: Dynamic/Private ports (temporary ports used by client-side applications)\n")
    input("\nPress Enter to return to the menu...")

def menu():
    clear_console()
    banner()
    while True:
        print("""
                   ======== Py-Scan ========
                    1. Scan one port
                    2. Scan multiple ports
                    3. Port usage information
                    x. Leave or return to menu
                   =========================
            """)
        choice = input("Please choose an option: ").lower()
        if choice == "x":
            break
        elif choice == "1":
            ip = get_ip()
            if ip:
                get_port_and_scan(ip)
        elif choice == "2":
            ip = get_ip()
            if ip:
                get_ports_and_scan(ip)
        elif choice == "3":
            port_usage_information()
        else:
            print("Invalid choice. Please enter 1, 2, 3 or x...")

menu()
