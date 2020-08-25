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
          console.log('Scuccessful')
        })
        .catch((error) => {
          console.log('error:', error.response)
        })
      this.$auth.loginWith('local', {
        data: registrationInfo,
      })
    },
  },
}
</script>
