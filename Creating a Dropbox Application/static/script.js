'use strict';
window.addEventListener('load', function () {
    document.getElementById('sign-out').onclick = function () {
        firebase.auth().signOut();
    };

    var uiConfig = {
        signInSuccessUrl: '/',
        signInOptions: [
            firebase.auth.GoogleAuthProvider.PROVIDER_ID,
            firebase.auth.EmailAuthProvider.PROVIDER_ID
        ]
    };

    firebase.auth().onAuthStateChanged(function (user) {
        if (user) {
            console.log(user);
            // User is signed in, so display the "sign out" button and login info.
            document.getElementById('sign-out').hidden = false;
            document.getElementById('user-content').hidden = false;
            console.log(`Signed in as ${user.displayName} (${user.email})`);
            user.getIdToken().then(function (token) {
                // Add the token to the browser's cookies.
                document.cookie = "token=" + token;
            });
        } else {
            // User is signed out.
            // Initialize the FirebaseUI Widget using Firebase.
            var ui = new firebaseui.auth.AuthUI(firebase.auth());
            // Show the Firebase login button.
            ui.start('#firebaseui-auth-container', uiConfig);
            // Update the login state indicators.
            document.getElementById('sign-out').hidden = true;
            document.getElementById('user-content').hidden = true;
            // Clear the token cookie.
            document.cookie = "token=";
        }
    }, function (error) {
        console.log(error);
        alert('Unable to log in: ' + error)
    });
});