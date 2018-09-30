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
.docs.markdown
  div(v-if="$route.params.name === 'simulator'")
    simulator
  div(v-else-if="$route.params.name === 'checklist'")
    preflight
    how-to-fly
    postflight
  div(v-else-if="$route.params.name === 'troubleshooting'")
    troubleshooting
  ul(v-else)
    li: router-link(to="/docs/checklist") Checklist
    li: router-link(to="/docs/simulator") Simulator
    li: router-link(to="/docs/troubleshooting") Troubleshooting
</template>


<script>
import HowToFly from '../../docs/how-to-fly.md'
import Simulator from '../../docs/simulator.md'
import Postflight from '../../docs/postflight.md'
import Preflight from '../../docs/preflight.md'
import Rules from '../../docs/rules.md'
import Troubleshooting from '../../docs/troubleshooting.md'

export default {
  components: {HowToFly, Simulator, Postflight, Preflight, Rules, Troubleshooting},
};
</script>


<style lang="postcss">
.docs {
  background: #fff;
  color: #000;
  min-height: 100vh;  /* Cover the whole page, for the background. */
  column-width: 400px;

  & table {
    border-collapse: collapse;
    width: 100%;
    margin-bottom: 1em;
    -webkit-column-break-inside: avoid;
    page-break-inside: avoid;
    break-inside: avoid-column;
  }

  & td {
    background: #fff;
    border: 1px solid #ddd;
  }

  & th {
    background: #000;
    color: #fff;
    text-transform: uppercase;
  }

  & td, & th {
    padding: 2px;
  }
}

@media print {

  .docs {
    & table {
      page-break-inside: avoid;
    }
  }
}
</style>
