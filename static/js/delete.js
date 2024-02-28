window.addEventListener("load", () => {
    delbuttons = document.querySelectorAll(".delete-button");
    for (let i = 0; i < delbuttons.length; i++) {
        delbuttons[i].addEventListener("click", () => deletePost(delbuttons[i].dataset.postId));
    }
});

async function deletePost(postId) {

    let data = {"id": postId};

    const response = await fetch("/api/post/delete", {
        method: "DELETE",
        headers: {"Content-Type": "application/json",},
        body: JSON.stringify(data)
    });

    if (response.ok || response.status == 404) {
        location.reload();
    }
}