document.addEventListener('DOMContentLoaded', function() {
    const loginButton = document.querySelector('.login');
    const registerButton = document.querySelector('.register');

    loginButton.addEventListener('click', function() {
        window.location.href = '/login/';
    });

    registerButton.addEventListener('click', function() {
        window.location.href = '/register/';
    });
});
