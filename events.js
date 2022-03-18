
document.addEventListener("submit", (event)=>{
    event.preventDefault()
    const search = document.getElementById("search-content")
    console.log(search.value);
})

const date =new Date()
document.getElementById("copyright").innerHTML = "Copy Right &copy "+date.getFullYear()

document.getElementById("search").addEventListener("click",()=>{
    window.location.href="./results.html"
})