<template>
  <div>
    <GraphD3></GraphD3>
  </div>
</template>

<script>
import GraphD3 from "@/components/GraphD3";

export default {
  name: "ConnectionPage",
  props:{
    msg:String
  },
  components:{
    GraphD3
  },
}
</script>

<style scoped>

</style>