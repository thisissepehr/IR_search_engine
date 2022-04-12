
// document.addEventListener("submit", (event)=>{
//     event.preventDefault()
//     const search = document.getElementById("search-content")
//     console.log(search.value);
// })

// setting the date at the end of the page
const date =new Date()
document.getElementById("copyright").innerHTML = "Copy Right &copy "+date.getFullYear()


// getting data by Clicking!
document.getElementById("search").addEventListener("click",(event)=>{
    //preventing from refrehing
    event.preventDefault()
    const search = document.getElementById("search-content").value

    // calling the server for this search query
    /////////////////////////////////////////////
    /////////////////////////////////////////////
    /////////////////////////////////////////////
    const data = getData(search)
    // console.log(search);
    //adding results
    let container = document.getElementById("results")
    
    clear_reasults(container);
    
    // populating the result area
    data.forEach((sample)=>{
        create_result_tile(sample, container)
    }) 
    container.style.visibility = "visible";
    // TODO: just a test remember to remove it
    // if (search ==="1"){

    //     data.forEach((sample)=>{
    //         create_result_tile(sample, container)
    //     })
    // }else if(search === "2"){
    //     data2.forEach((sample)=>{
    //         create_result_tile(sample, container)
    //     })
    // }

})

let clear_reasults = (container)=>{
    while(container.firstChild) {
        container.removeChild(container.firstChild);
    }      
}
let create_result_tile = (sample, container)=> {
    
    // create card
    let inside_div= document.createElement('div')
    inside_div.classList.add("point")
    
    //adding title
    let title_a = document.createElement('a')
    title_a.classList.add("title-with-link")
    title_a.href = sample.url
    title_a.innerHTML = sample.title
    inside_div.prepend(title_a)
    let author_year = document.createElement('div')
    author_year.classList.add("author-year")
    let authors =""
    sample.author.forEach((auth)=>{
        authors += auth
        authors += ", "
    })
    let p_author = document.createElement('p')
    p_author.innerHTML = authors.substring(0,authors.length-2)

    let p_year = document.createElement('p')
    p_year.innerHTML = sample.year

    author_year.append(p_author)
    author_year.append(p_year)

    inside_div.append(author_year)
    
    container.append(inside_div)
}

let getData = (query)=>{
    let dataRecieved = []
    fetch("?query="+query).then((response)=>{
        response.json().then((data)=>{
            if (data.error){

            }else{
                dataRecieved = data
            }
        })
    })
    console.log(dataRecieved)
    return dataRecieved;

}



const data2= [
    {
        title:"something 1000",
        author:["john Doe", "sep"],
        url:"https://google.com",
        year: 2022
    },
    {
        title:"something 2000",
        author:["jane Doe"],
        url:"https://google.com",
        year: 2021
    },
    {
        title:"something 3000",
        author:["sep Doe"],
        url:"https://google.com",
        year: 1982
    },
    {
        title:"something 4000",
        author:["alex Doe"],
        url:"https://google.com",
        year: 2022
    },
    
]


const data= [
    {
        title:"something 1",
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