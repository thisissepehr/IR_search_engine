const data= [
    {
        title:"something 1",
        author:"john Doe",
        url:"https://google.com",
        doi:"ASEDTV4899489"
    },
    {
        title:"something 2",
        author:"jane Doe",
        url:"https://google.com",
        doi:"ASEDTV4899489"
    },
    {
        title:"something 3",
        author:"sep Doe",
        url:"https://google.com",
        doi:"ASEDTV4899489"
    },
    {
        title:"something 4",
        author:"alex Doe",
        url:"https://google.com",
        doi:"ASEDTV4899489"
    },
]

let container = document.getElementById("holder")
// document.removeChild(container)
// container = document.createElement("div")
// container.id = "holder"
// container.classList.add("result-container")
data.forEach((sample)=>{
    let inside_div= document.createElement('div')
    inside_div.classList.add("point")
    let p = document.createElement('p')
    p.innerHTML = sample.title
    inside_div.prepend(p)
    let aa = document.createElement('a')
    aa.href = sample.url
    aa.innerHTML = "download"
    inside_div.append(aa)
    let ppp = document.createElement('p')
    ppp.innerHTML = sample.doi
    inside_div.append(ppp)
    
    
    container.prepend(inside_div)


})