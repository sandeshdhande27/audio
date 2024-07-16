const express = require('express');
const net = require('net');

const http = require('http');
const socketIo = require('socket.io');
const path = require('path');
const app = express();
const server = http.createServer(app);
const io = socketIo(server);

app.use(express.static(__dirname + '/'));
// Serve the index.html file at the root path
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'index.html'));
});

// Create a server instance
const server2 = net.createServer((socket) => {
    // 'socket' is a duplex stream that represents the connection to a client

    // Handle incoming data from clients
    socket.on('data', (data) => {
        console.log(`Received from client: ${data}`);
        io.emit('chat message', `Received from client: ${data}`);
        
    });

    // Handle client connection closed
    socket.on('end', () => {
        console.log('Client disconnected');
    });

    // Handle errors
    socket.on('error', (err) => {
        console.error('Socket error:', err);
    });
});

// Start listening on a specific port and IP address
const port = 5004;
const host = '127.0.0.1';
server2.listen(port, host, () => {
    console.log(`Server started on ${host}:${port}`);
});


io.on('connection', (socket) => {
    console.log('a user connected');
    socket.on('msg', (data) => {
        console.log('user //////////////// disconnected');
    });
    socket.on('disconnect', () => {
        console.log('user is disconnected');
    });
    socket.on('error', (e) => {
        console.log('user disconnected',e);
    });
    socket.on('stoptest', (msg) => {
        // Create a client socket
        const client = new net.Socket();
        const SERVER_IP = '127.0.0.1';
        const SERVER_PORT = 5003;
        // Connect to the server
        client.connect(SERVER_PORT, SERVER_IP, () => {
        console.log(`Connected to server at ${SERVER_IP}:${SERVER_PORT}`);
        
        // Send data to the server
        const data = msg;
        client.write(data);
        client.destroy(); // kill client after server's response
        console.log(`Data sent: ${data}`);
        });   
        client.on('error', (err) => {
            if (err.code === 'ECONNREFUSED') {
              console.error(`Connection refused at ${err.address}:${err.port}`);
              // Handle the error accordingly
            } else {
              console.error('An error occurred:', err);
            }
          });
    });
    socket.on('starttest', (msg) => {
        // Create a client socket
        const client = new net.Socket();
        const SERVER_IP = '127.0.0.1';
        const SERVER_PORT = 5003;
        // Connect to the server
        client.connect(SERVER_PORT, SERVER_IP, () => {
        console.log(`Connected to server at ${SERVER_IP}:${SERVER_PORT}`);
        
        // Send data to the server
        const data = msg;
        client.write(data);
        client.destroy(); // kill client after server's response
        console.log(`Data sent: ${data}`);
        });   
        client.on('error', (err) => {
            if (err.code === 'ECONNREFUSED') {
              console.error(`Connection refused at ${err.address}:${err.port}`);
              // Handle the error accordingly
            } else {
              console.error('An error occurred:', err);
            }
          });
    });
    socket.on('stopall', (msg) => {
        console.log('1233333333')
        // Create a client socket
        const client = new net.Socket();
        const SERVER_IP = '127.0.0.1';
        const SERVER_PORT = 5003;
       
            client.connect(SERVER_PORT, SERVER_IP, () => {
                console.log(`Connected to server at ${SERVER_IP}:${SERVER_PORT}`);
                
                // Send data to the server
                const data = msg;
                client.write(data);
                client.destroy(); // kill client after server's response
                console.log(`Data sent: ${data}`);
                });   
                client.on('error', (err) => {
                    if (err.code === 'ECONNREFUSED') {
                      console.error(`Connection refused at ${err.address}:${err.port}`);
                      // Handle the error accordingly
                    } else {
                      console.error('An error occurred:', err);
                    }
                  });
        // Connect to the server
        
    });
    socket.on('chat message', (msg) => {
        console.log('message: ' + msg);
        const SERVER_IP = '127.0.0.1';
        const SERVER_PORT = 5003;

        // Create a client socket
        const client = new net.Socket();

        // Connect to the server
        client.connect(SERVER_PORT, SERVER_IP, () => {
        console.log(`Connected to server at ${SERVER_IP}:${SERVER_PORT}`);
        
        // Send data to the server
        const data = msg;
        client.write(data);
        client.destroy(); // kill client after server's response
        console.log(`Data sent: ${data}`);
        });
        client.on('error', (err) => {
            if (err.code === 'ECONNREFUSED') {
              console.error(`Connection refused at ${err.address}:${err.port}`);
              // Handle the error accordingly
            } else {
              console.error('An error occurred:', err);
            }
          });
        io.emit('chat message', msg);
    });
});

server.listen(3000, () => {
    console.log('listening on *:3000');
});
