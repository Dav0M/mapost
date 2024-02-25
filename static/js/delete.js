window.addEventListener("load", ()=>{
    delbuttons = document.querySelectorAll(".delete-button");
    for(let i = 0; i<delbuttons.length; i++) {
        delbuttons[i].addEventListener("click", ()=> deletePost(delbuttons[i]));
    }
});

async function deletePost(node) {
    const postRow = node.parentNode.parentNode.parentNode;

    let data = {"id": postRow.id};

    const response = await fetch("/api/post", {
        method: "DELETE",
        headers: {"Content-Type": "application/json",},
        body: JSON.stringify(data)
    });

    if (response.ok || response.status == 404) {
        postRow.remove();
    }
}