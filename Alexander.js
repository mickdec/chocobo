const express = require('express');
const app = express();
const http = require('http');
const server = http.createServer(app);
const { Server } = require("socket.io");
const io = new Server(server);

DATA = {}
update = false

app.use(express.json());
app.use(express.static(__dirname + '/views/'));
app.use(express.urlencoded({ extended: true }))

io.on('connection', (socket) => {
    if (update) {
        console.log(DATA)
        io.emit("Update", DATA)
        DATA = {}
        update = false
    }
    socket.on('Update', () => {
        if (update) {
            console.log(DATA)
            io.emit("Update", DATA)
            DATA = {}
            update = false
        }
    });
});

app.get('/', async (req, res) => {
    res.sendFile('views/index.html', { root: __dirname })
})

app.post('/add_exploit', (req, res) => {
    

    DATA = {...DATA,...req.body}

    console.log(DATA)
    update = true
    res.send("OK")
})

server.listen(80, (req, res) => {
});

