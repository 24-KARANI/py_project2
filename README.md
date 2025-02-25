Security project 2

TCP Proxy

Overview:

This TCP proxy is a simple Python tool designed to intercept and forward traffic between a client and a remote host. Built as part of my resume projects, it works in tandem with my custom netcat clone (first project) to test interactive shells and network communications.
Features:

• Logs intercepted data in hexdump format. 
• Provides hooks (request_handler and response_handler) for modifying traffic. 
• Supports a "receive-first" mode to capture initial remote banners or prompts. 
• Uses multi-threading to handle multiple simultaneous connections.

Prerequisites:

• Python 3.x
Files Included:

    proxy.py - The TCP proxy script.
    clone_netcat.py - My custom netcat clone for testing (used as both server and client).

Usage Instructions:

    Start the Netcat Clone Listener: In one terminal, launch the netcat clone in listener mode (with an interactive command shell) by running:

python3 clone_netcat.py -t 192.168.1.101 -p 5555 -l -c

This will start the remote shell on IP 192.168.1.101, port 5555.

Launch the TCP Proxy: In another terminal, start the proxy. 
For example, to have the proxy listen on IP 192.168.1.101, port 9000 and forward traffic to the netcat listener (192.168.1.101:5555) with receive-first mode enabled, run:

python3 proxy.py 192.168.1.101 9000 192.168.1.101 5555 True

Connect as a Client via the Proxy: In a third terminal, use the netcat clone to connect to the proxy instead of directly to the listener:

    python3 clone_netcat.py -t 192.168.1.101 -p 9000

    Once connected, your commands will be routed through the proxy to the remote shell, and you'll see the command shell output in your client terminal.

Additional Notes:

• Set the "receive-first" flag to True if the remote service sends an initial banner or prompt. 
• If the proxy closes connections too quickly during interactive sessions, consider adjusting the idle timeout conditions within the code. 
• Customize the data handlers (request_handler and response_handler in proxy.py) to alter or log traffic as needed.
