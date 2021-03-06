const path = require("path")
const express = require("express")
const hbs = require('hbs')
const {spawn} = require("child_process")
const fs = require('fs')

const getResults = (index)=>{
    try {
        const data = fs.readFileSync('../py/results'+index+'.txt', 'utf8')
        return(data)          

      } catch (err) {
        console.error(err)
      }
}



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

let index = 1;
app.get("/search",async(req,res)=>{
    if(!req.query.query || !req.query.method) {
        return res.send({
            data: [{
                title:"Error in your search",
                author:["error"],
                url:"/",
                year: 0        
            }]
        })
    }
    // const python = spawn('python3',['./utils/searchConnector.py',req.query.query, req.query.method])
    // 

    // dataTosend = ''

    // await python.stdout.on('data', (data)=>{
    //     dataTosend += data.toString();
    // });

    // python.on('close', (code)=>{
    //     res.send({
    //         data: eval(dataTosend)
    //     })
    // })
    res.send({
        data: eval(getResults(index))
    })
    index++;
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

