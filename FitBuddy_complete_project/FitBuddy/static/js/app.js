function confirmDelete(){return window.confirm("Delete this user and their saved plans?");}
document.addEventListener("DOMContentLoaded",()=>{document.querySelectorAll("form").forEach(f=>f.addEventListener("submit",()=>{const b=f.querySelector("button[type=submit]");if(b&&!b.classList.contains("danger")){b.disabled=true;b.textContent="Working..."}}))});
