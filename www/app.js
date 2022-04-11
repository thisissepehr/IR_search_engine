const path = require("path")
const express = require("express")


// defining paths to pages
const publicDirectoryPath = path.join(__dirname,'public')


const app = express()
const port = process.env.PORT || 3000


app.use(express.static(path.join(publicDirectoryPath)))


app.get("", (req,res)=>{
    res.sendFile(publicDirectoryPath+"/html/index.html")
})
app.listen(port, ()=>{
    console.log("server is up on port "+port);
})