
document.addEventListener("submit", (event)=>{
    event.preventDefault()
    const search = document.getElementById("search-content")
    console.log(search.value);
})