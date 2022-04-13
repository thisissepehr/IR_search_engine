
// setting the date at the end of the page
const date =new Date()
document.getElementById("copyright").innerHTML = "Copy Right &copy "+date.getFullYear()


// getting data by Clicking!
document.getElementById("search").addEventListener("click",(event)=>{
    //preventing from refrehing
    event.preventDefault()
    const search = document.getElementById("search-content").value
    const methodToUse = getMethodValue();

    //adding results
    let container = document.getElementById("results")
    clear_reasults(container);

    // get results from the server and populate the container
    const data = getData(search, methodToUse,container);

    // make it visible once the results are prepared
    container.style.visibility = "visible";
})

let getMethodValue = ()=>{
    const radioButtons = document.querySelectorAll('input[name="method"]');
    let selectedSize;
            for (const radioButton of radioButtons) {
                if (radioButton.checked) {
                    selectedSize = radioButton.value;
                    break;
                }
            }
    return selectedSize
}

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

let getData = (query,methodTouse, container)=>{
    let dataRecieved = []
    fetch("/search?query="+query+"&method="+methodTouse).then((response)=>{
        response.json().then((data)=>{
            if (data.error){

            }else{
                dataRecieved = data.data
                // populating the result area
                dataRecieved.forEach((sample)=>{
                    create_result_tile(sample, container)
                }) 
            }
        })
    })
    return dataRecieved;

}


