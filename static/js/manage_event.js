let attendee_status = document.getElementsByClassName("attendee_status");
let remove_invites = document.getElementsByClassName("remove_invite");
const update_attendee_endpoint = document.getElementById("update_attendee_endpoint").value;
const send_invite_btn = document.getElementById("send_invites");
const send_invites_endpoint = document.getElementById("send_invites_endpoint").value;
let invite_emails = document.getElementsByClassName("invite-email");


// send_invite_btn.onclick = (e)=>{
//     if(confirm("Are you sure you want to send out invites to those who have not recieved one yet?")){
//         fetch(send_invites_endpoint, {
//             method: 'POST',
//             headers: {
//                 "X-CSRFToken": getCookie('csrftoken'),
//                 'Content-Type': 'application/json'
//             },
//         })
//       .then(response => {
//         if(response.ok){
//             console.log(response)
//             window.location.reload();
//             alert("emails sent!")
//         }
//       })
//     }
// }

for(let i = 0; i < attendee_status.length; i++){
    attendee_status[i].addEventListener("change", function(e){
        data = {
            "status": this.value,
            "pk": this.getAttribute("pk"),
            "action": "status"
        }
        console.log(update_attendee_endpoint)
        fetch(update_attendee_endpoint, {
            method: 'POST',
            headers: {
                "X-CSRFToken": getCookie('csrftoken'),
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data),
        })
      .then(response => console.log(response))
    })
}


// CHANGE EMAIL DYNAMICALLY
for(let i = 0; i < invite_emails.length; i++){
    invite_emails[i].addEventListener("change", function(e){
        data = {
            "email": this.value,
            "pk": this.getAttribute("pk"),
            "action": "email"
        }
        console.log(update_attendee_endpoint)
        fetch(update_attendee_endpoint, {
            method: 'POST',
            headers: {
                "X-CSRFToken": getCookie('csrftoken'),
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data),
        })
        .then(response => response.text())
        .then(data => {
          console.log(data)
        })
    })
}





for(let i = 0; i < remove_invites.length; i++){
    remove_invites[i].addEventListener("click", function(e){
        if(!confirm("Are you sure you want to remove this invite?")){
            return;
        }
        data = {
            "pk": this.getAttribute("pk"),
            "action": "remove"
        }
        fetch(update_attendee_endpoint, {
            method: 'POST',
            headers: {
                "X-CSRFToken": getCookie('csrftoken'),
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data),
        })
      .then(response => {
        if (response.ok){
            this.parentNode.parentNode.remove()
        }
      })
    })
}

let name_input = document.getElementById("nameInput");
let password_input = document.getElementById("passwordInput");
let save_form = document.getElementById("saveForm")
let email_template = document.getElementById("email_template")
let email_subject = document.getElementById("email_subject")

name_input.addEventListener("focusout", function(e){
    saveData(name_input.value, password_input.value, email_template.value, email_subject.value)
    eventName.innerHTML = name_input.value;
})
password_input.addEventListener("focusout", function(e){
    saveData(name_input.value, password_input.value, email_template.value, email_subject.value)
})

email_template.addEventListener("change", function(e){
    saveData(name_input.value, password_input.value, email_template.value, email_subject.value)
})

email_subject.addEventListener("change", function(e){
    saveData(name_input.value, password_input.value, email_template.value, email_subject.value)
})


function saveData(name, password, email_template, email_subject) {
    const data = { name, password, email_template, email_subject};

    fetch(save_form.getAttribute("action"), {
        method: 'POST',
        headers: {
            "X-CSRFToken": getCookie('csrftoken'),
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data),
    })
    .then(data => console.log('Data saved successfully:', data))
    .catch(error => console.error('Error saving data:', error));
}

if (document.getElementById('stop_outreach')) {
    // Refresh the page every 5 seconds (5000 milliseconds)
    setTimeout(function() {
        window.location.reload();
    }, 5000);
}