<template>
  <div id="main">
    <el-container direction="vertical">
      <Header msg="基于知识图谱的金融实体关系关联计算系统"></Header>
      <el-main><router-view/></el-main>
    </el-container>
  </div>

</template>

<script>

import Header from "@/components/Header"

export default {
  name: "Main",
  components: {
    // HelloWorld,

    Header
  },


}
</script>

<style scoped>
#main{
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;

  position: fixed;
  display: flex;
  width: 100%;
  height: 100%;
}
</style>