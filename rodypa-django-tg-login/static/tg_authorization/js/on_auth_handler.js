/*
Handle call of onTelegramAuth from the login widget.
*/

let telegramIdInput;
document.addEventListener("DOMContentLoaded", () => {
    telegramIdInput = document.querySelector('.telegram_id_input');

    function onTelegramAuth(user) {
        telegramIdInput.value = user.id;
    };
}
)