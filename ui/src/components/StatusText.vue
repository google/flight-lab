<!-- 
  Copyright 2018 Flight Lab authors.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

  https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
 -->

<template lang="pug">
span(:class="className") {{status}}
</template>

<script>
export default {
  props: ['status'],
  computed: {
    className(){
      if (this.status === 'ON' || this.status === 'RUNNING') return 'primary--text';
      else if (this.status === 'OFF' || this.status === 'NOT_RUNNING') return 'grey--text';
      else return 'warning--text';
    },
    text() {

    }
  }
};
</script>

<style scoped>

</style>
