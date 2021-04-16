const usernameField=document.querySelector('#usernameField');
const feedBackArea=document.querySelector('#invalid_feedback');
const emailFeedBackArea=document.querySelector('#invalid_email_feedback');
const emailField=document.querySelector('#emailField');
const usernameSuccessOutput=document.querySelector('.usernameSuccessOutput');
const passwordField=document.querySelector('#passwordField');
const showPassToggle = document.querySelector('.showPassToggle');
const submitBtn = document.querySelector('.submitBtn');

usernameField.addEventListener("keyup", (e) => {
    const usernameVal = e.target.value;
    usernameSuccessOutput.textContent=`Checking ${usernameVal}`;
    usernameField.classList.remove("is-invalid");
    feedBackArea.style.display = 'block';
    feedBackArea.innerHTML=`<p> </p>`;

  if (usernameVal.length > 0) {
    fetch("/authentication/validate-username", {
        body: JSON.stringify({ username: usernameVal }),
        method: "POST",
    })
        .then((res)   => res.json())
        .then((data)  => {
            console.log("data", data);
            if (data.username_error){
                submitBtn.disabled = true;
                usernameField.classList.add("is-invalid");
                usernameSuccessOutput.style.display='none';
                feedBackArea.style.display = 'block';
                feedBackArea.innerHTML=`<p> ${data.username_error} </p>`;
            }
            else{
                submitBtn.removeAttribute("disabled")
            }
    });
   }
});

emailField.addEventListener("keyup", (e) => {
    const emailVal = e.target.value;
    emailField.classList.remove("is-invalid");
    emailFeedBackArea.style.display = 'block';
    emailFeedBackArea.innerHTML=`<p> </p>`;

  if (emailVal.length > 0) {
    fetch("/authentication/validate-email", {
        body: JSON.stringify({ email: emailVal }),
        method: "POST",
    })
        .then((res)   => res.json())
        .then((data)  => {
            console.log("data", data);
            if (data.email_error){
                submitBtn.disabled = true;
                emailField.classList.add("is-invalid");
                emailFeedBackArea.style.display = 'block';
                emailFeedBackArea.innerHTML=`<p> ${data.email_error} </p>`;
            }
            else{
                submitBtn.removeAttribute("disabled");
            }
    });
   }
});


const handleToggleInput = (e) => {
    if (showPassToggle.textContent === "Show"){
        showPassToggle.textContent = "Hide";
        passwordField.setAttribute("type","text");
    }
    else {
        showPassToggle.textContent = "Show";
        passwordField.setAttribute("type","password");

    }
};

showPassToggle.addEventListener("click", handleToggleInput);