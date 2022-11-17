<template>
  <div id="Header">
    <el-row>
      <el-col id="logo"></el-col>
<!--      <el-col :span="4" :offset="4">金融实体关系关联计算系统</el-col>-->
      <el-col id="menu">
        <el-menu  class="el-menu-demo" mode="horizontal" @select="handleSelect">
          <el-menu-item index="1">关系搜索</el-menu-item>
          <el-menu-item index="2">关联方</el-menu-item>
          <el-menu-item index="3">股权结构</el-menu-item>
        </el-menu>
      </el-col>
    </el-row>
  </div>
</template>

<script>
export default {
  name: "Header",
  props: {
    msg:String
  },
  data(){
    return{
      activeIndex: '1',
      clickType: NaN,
      clickPath: undefined,
    }
  },
  methods: {
    handleSelect(key, keyPath) {
      this.$store.commit('updateClickType', keyPath);
      console.log(key, keyPath)
      if(keyPath[0] === '1'){
        this.clickType = 'showRelationshipPage';
        this.$router.push({path:'relationship'});
      }
      else if(keyPath[0] === '2'){
        this.clickType = 'showRelatedPartiesPage';
        this.$router.push({path:'relatedparty'});
      }
      else if(keyPath[0] === '3'){
        this.clickType = 'showRelatedPartiesPage';
        this.$router.push({path:'shareholding'});
      }
      // if (keyPath[0] === "5" || keyPath[0] === "8") {
      //   this.$store.commit('showMainGraph', true);
      // } else {
      //   this.$store.commit('showMainGraph', false);
      // }
    }
  }
}
</script>

<style scoped>
#Header{
  /*background-color: #99BCD6;*/
  /*color: #032946;*/
  /*text-align: center;*/
  line-height: 80px;
  border-bottom: solid 1px #e6e6e6;
  /*font-size: 38px;*/
}
.el-col{
  height: 110px;
  /*width: 9px;*/
  display:table-cell;
  vertical-align:bottom;
}
.el-menu{
  margin-top: 50px;
}
.el-menu-item{
  font-size: 18px;
  padding-left: 30px;
  padding-right: 30px;
}
#menu{
  width: 40%;
}
#logo{
  width: 60%;
  background: url('../assets/logo.jpg') center top no-repeat;
  background-size: 90% 100%;
}

</style>