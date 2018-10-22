let ip = location.host;
let port = 80;
if(ip.includes(":")){
    [ip, port] = ip.split(":")[0];
}
export const IP = ip;
export const PORT = port;

// export const IP = "172.16.0.110"
// export const PORT = 5000
