
document.addEventListener("submit", (event)=>{
    event.preventDefault()
    const search = document.getElementById("search-content")
    console.log(search.value);
})

// setting the date at the end of the page
const date =new Date()
document.getElementById("copyright").innerHTML = "Copy Right &copy "+date.getFullYear()

document.getElementById("search").addEventListener("click",()=>{
    
    let container = document.getElementById("results")
    // document.removeChild(container)
    // container = document.createElement("div")
    // container.id = "holder"
    // container.classList.add("result-container")
    container.style.visibility = "visible";
    data.forEach((sample)=>{
        create_result_tile(sample, container)
    })

})


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

