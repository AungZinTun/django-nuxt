The tutorial has been split into two parts- setting up the backend, and setting up the frontend. This is Part-2.

The repo has two branches: `part-1` and `part-2`. `part-1` contains the files for this tutorial, `part-2` contains
the files for this tutorial and the next.

**Tutorial Part 1:** [Here](https://dev.to/ignisda/setting-up-user-authentication-with-nuxtjs-and-django-rest-framework-5ge2-temp-slug-5352206?preview=528ce6b1b427d419125d4c7a35e4b00260bc1199be76516054cb9046f56ec6aa9abaeb1f7399bf23a6bb4de60be5bd28dfc75656c04bd78f7e9cce9b)

**GITHUB REPO:** https://github.com/IgnisDa/django-nuxtjs-authentication

**NOTE:** I will omit most of the HTML to maintain brevity. You can
consult the repository to see the complete files.

# Prerequisites

1. Familiarity with django-rest-framework
2. Knowledge of nuxt-auth: [this video will be enough](https://m.youtube.com/watch?v=zzUpO8tXoaw)

# Setting up the frontend

If you want to integrate authentication to an existing project, add
the required modules to your project using `npm` or `yarn`. Just run `npm install @nuxtjs/auth @nuxtjs/axios` in the `frontend/` directory.

If you're starting from scratch, you can follow these steps.

```bash
$ npx create-nuxt-app frontend # in the root directory `nuxtjs+drf-user-auth/`

Generating Nuxt.js project in frontend
? Project name: frontend
? Programming language: JavaScript
? Package manager: Npm
? UI framework: Vuetify.js
? Nuxt.js modules: Axios
? Linting tools: ESLint, Prettier
? Testing framework: Jest
? Rendering mode: Single Page App
? Deployment target: Server (Node.js hosting)
? Development tools: jsconfig.json (Recommended for VS Code if you're not using typescript)
```

I will be using Vuetify as my UI framework, but you are free to use whatever
else you want. However, be aware that if you use something else (like
Buefy), you will have to use different HTML tags. For example, a button in Vuetify `<v-btn @click="greetPerson()">Click Me!</v-btn>` will be
written as `<b-button @click="greetPerson()">Click Me!</b-button>` in
Buefy. The Vue directives and general API, however, remain the same.

First we'll configure our settings to use the auth-module.

```javascript
// frontend/nuxtjs.config.js
export default {
// [...other settings...]
    modules:{
        // [...other stuff...]
       '@nuxtjs/axios',
       '@nuxtjs/auth',
   },
    axios: {
       baseURL: 'http://127.0.0.1:8000/',
   },
    auth: {
    strategies: {
      local: {
        endpoints: {
          login: {
            url: 'token/login/',
            method: 'post',
            propertyName: 'auth_token',
          },
          logout: { url: 'token/logout/', method: 'post' },
          user: {
            url: 'accounts/data/',
            method: 'get',
            propertyName: false,
          },
        },
        tokenType: 'Token',
        tokenName: 'Authorization',
      },
      redirect: {
        login: '/login',
        home: '/',
      },
    },
  },
}
```

Then create a file `frontend/store/index.js` and save it. Fire up a
development server using by running `npm run dev` in the `frontend/`
directory. Visit `http://127.0.0.1:3000/` in your browser.

Here is what we did:

1. Added the `axios` module to our setup. This module can be best compared to the `requests` package that we often use in python.
2. Added the `auth` module to our setup that will automatically send the required requests to the backend for user authentication.
3. We store the currently logged-in user's data in the [Vuex](https://vuex.vuejs.org/) store. So we created `frontend/store/index.js` to activate this module.

We will make a few changes in `frontend/layouts/default.vue`.s

```HTML
<!-- layouts/default.vue -->
<!-- Add these lines somewhere near the middle so that these buttons are visible on the navbar -->
<template>
<!-- Other stuff -->
   <div class="authentication-buttons">
      <div v-if="$auth.loggedIn">
         {{ $auth.user.email }}
         <v-btn icon to="/logout" class="logout-btn">
            <v-icon light @click="$auth.logout()">mdi-logout</v-icon>
         </v-btn>
      </div>
      <div v-else>
         <v-btn icon to="/login" class="login-btn">
            <v-icon>mdi-login</v-icon>
         </v-btn>
         <v-btn icon to="/register" class="register-btn">
            <v-icon>mdi-account-key-outline</v-icon>
         </v-btn>
      </div>
   </div>
<!-- Other stuff -->
</template>

<script>
export default {
  // Some more stuff
}
</script>
```

We used the `v-if` directive to check if the current user is logged-in.
If there is, then display a _logout_ button, else display _login_ and
_register_ buttons using the `v-else` directive.

Next, let's make pages (routes) for _login_, _logout_, and _register_.

```HTML
<!-- pages/login.vue -->
<!-- This contains the login form. You should also add some custom validation yourself. -->
<template>
  <div class="login-page">
    <v-layout flex align-center justify-center>
      <v-flex xs6 sm6 elevation-6>
        <v-card>
          <v-card-title flex align-center justify-center>
            <h1>Login</h1>
          </v-card-title>
          <v-card-text class="pt-4">
            <div>
              <v-form ref="form">
                <v-text-field
                  v-model="userData.email"
                  label="Enter your e-mail address"
                  counter
                  required
                ></v-text-field>
                <v-text-field
                  v-model="userData.password"
                  label="Enter your password"
                  :append-icon="
                    userData.showPassword ? 'mdi-eye-off' : 'mdi-eye'
                  "
                  :type="userData.showPassword ? 'text' : 'password'"
                  required
                  @click:append="userData.showPassword = !userData.showPassword"
                ></v-text-field>
                <v-layout justify-space-between>
                  <v-btn @click="logInUser(userData)">
                    Login
                  </v-btn>
                  <a href="?">Forgot Password</a>
                </v-layout>
              </v-form>
            </div>
          </v-card-text>
        </v-card>
      </v-flex>
    </v-layout>
  </div>
</template>

<script>
export default {
  data: () => ({
    userData: { email: '', password: '', showPassword: false },
  }),
  methods: {
    async logInUser(userData) {
      try {
        await this.$auth.loginWith('local', {
          data: userData,
        })
        console.log('notification successful')
      } catch (error) {
        console.log('notification unsuccessful')
      }
    },
  },
}
</script>
```

In this page, we created a login form with `email` and `password` fields.
There is a `data` object that stores all properties of the form so that
we can perform validation on it, and send that validated data to the
backend. On clicking the button labelled _Login_, an async function
`logInUser()` is executed. This uses the Nuxtjs `auth` module to send a
POST request containing the `userData` to `token/login/` which will then
automatically perform the login and return the login token as
`auth_token`. This `auth_token` is stored in the Vuex store for further use
later. Furthermore, a new request is sent to `accounts/data/` which then
returns all the data about the logged in user like `email`, `id`, `first_name`,
etc. The _logout_ button already works. When you click on it, it calls an `auth`
module function- `$auth.logout()`. This simply deletes the `auth_token` from
memory and flushes out the `$auth.user` object.

So _login_ and _logout_ functionalities are working! Yay!

Let's get the _registration_ functionality working now. This will be fairly
easy.

```HTML
<!-- pages/register.vue -->
<template>
  <div class="register-page">
    <v-container>
      <v-layout flex align-center justify-center>
        <v-flex xs6 sm6 elevation-6>
          <v-card>
            <v-card-title flex align-center justify-center>
              <h1>Register</h1>
            </v-card-title>
            <v-card-text class="pt-4">
              <div>
                <v-form ref="form">
                  <v-text-field
                    v-model="userData.email"
                    label="Enter your e-mail address"
                    counter
                    required
                  ></v-text-field>
                  <v-text-field
                    v-model="userData.password"
                    label="Enter your password"
                    required
                    :append-icon="
                      userData.showPassword ? 'mdi-eye' : 'mdi-eye-off'
                    "
                    :type="userData.showPassword ? 'text' : 'password'"
                    @click:append="
                      userData.showPassword = !userData.showPassword
                    "
                  ></v-text-field>
                  <v-text-field
                    v-model="userData.password2"
                    label="Confirm password"
                    :append-icon="
                      userData.showPassword2 ? 'mdi-eye' : 'mdi-eye-off'
                    "
                    :type="userData.showPassword2 ? 'text' : 'password'"
                    required
                    @click:append="
                      userData.showPassword2 = !userData.showPassword2
                    "
                  ></v-text-field>
                  <v-layout justify-space-between>
                    <v-btn @click="signUp(userData)">
                      Register
                    </v-btn>
                    <a href="">Forgot Password</a>
                  </v-layout>
                </v-form>
              </div>
            </v-card-text>
          </v-card>
        </v-flex>
      </v-layout>
    </v-container>
  </div>
</template>

<script>
export default {
  data: () => ({
    userData: {
      email: '',
      password: '',
      password2: '',
      showPassword: false,
      showPassword2: false,
    },
  }),
  methods: {
    signUp(registrationInfo) {
      this.$axios
        .$post('accounts/users/', registrationInfo)
        .then((response) => {
          console.log('Successful')
        })
        .catch((error) => {
          console.log('errors:', error.response)
        })
      this.$auth.loginWith('local', {
        data: registrationInfo,
      })
    },
  },
}
</script>
```

As soon as the user enters their details in the form, and click the _Register_
button, a function `signUp()` is fired. Using the `axios` module, a POST
request is sent to `accounts/users`. Assuming the data is valid, the user is
created in the database. Next, we use the `auth` module to again login using
the same logic as we did previously in our login page `login.vue`. _Logout_
functionality stays the same as before.

# Conclusion

So, now that you are with authentication what new feature do you plan to
implement?

I thank you all for taking the time to follow this tutorial and I hope I can
help you again in future. See you!
