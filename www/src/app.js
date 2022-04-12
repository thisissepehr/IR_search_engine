const path = require("path")
const express = require("express")
const hbs = require('hbs')


// defining paths to pages
const publicDirectoryPath = path.join(__dirname,'../public')
const viewsPath = path.join(__dirname, '../templates/views')
const partialsPath = path.join(__dirname, '../templates/partials')


const app = express()
const port = process.env.PORT || 3000

//define paths to files
app.use(express.static(path.join(publicDirectoryPath)))

//setup handlebars as our view engine and views location
app.set('view engine', 'hbs')
app.set('views', viewsPath)
hbs.registerPartials(partialsPath)

app.use(express.static(publicDirectoryPath))


app.get("", (req,res)=>{
    res.render("index", {})
})

app.get("/search",(req,res)=>{
    if(!req.query.query) {
        return res.send({
            error: "Provide some text to start the search"
        })
    }

    // this is the place to call the pythonic functions
    ///////////////////////////////////////////////////
    //                                               //
    //                 Python code call              //
    //                                               //
    ///////////////////////////////////////////////////
    res.send({
        data: data1
    })
})


app.listen(port, ()=>{
    console.log("server is up on port "+port);
})



const data1= [
    {
        title:"something 10000",
        author:["john Doe", "sep"],
        url:"https://google.com",
        year: 2022
    },
    {
        title:"something 2",
        author:["jane Doe"],
        url:"https://google.com",
        year: 2021
    },
    {
        title:"something 3",
        author:["sep Doe"],
        url:"https://google.com",
        year: 1982
    },
    {
        title:"something 4",
        author:["alex Doe"],
        url:"https://google.com",
        year: 2022
    },
    
]

