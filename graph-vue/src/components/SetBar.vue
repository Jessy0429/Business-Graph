<template>
  <div id="SetBar">
    <el-row v-if="(this.path === 0)" key="0">
      <el-col :span="4" :offset="4">
        <el-input
            placeholder="请输入内容"
            v-model="source"
            clearable>
        </el-input>
      </el-col>
      <el-col :span="4" :offset="1">
        <el-input placeholder="请输入内容" v-model="target" clearable></el-input>
      </el-col>
      <el-col :span="1" :offset="1">
        <el-button type="primary" round @click="search">搜索</el-button>
      </el-col>
    </el-row>

    <el-row v-if="(this.path === 1)" key="1">
      <el-col :span="4" :offset="4">
        <el-input
            placeholder="请输入内容"
            v-model="source"
            clearable>
        </el-input>
      </el-col>
      <el-col :span="4" :offset="1">
        <el-select v-model="searchRelation" multiple placeholder="关联方种类">
          <el-option
              v-for="item in relationList"
              :key="item.value"
              :label="item.label"
              :value="item.value">
          </el-option>
        </el-select>
      </el-col>
      <el-col :span="1" :offset="1">
        <el-button type="primary" round @click="search">搜索</el-button>
      </el-col>
    </el-row>

    <el-row v-if="(this.path === 2) || (this.path === 3)" key="2">
      <el-col :span="4" :offset="4">
        <el-input
            placeholder="请输入内容"
            v-model="source"
            clearable>
        </el-input>
      </el-col>
      <el-col :span="1" :offset="1">
        <el-button type="primary" round @click="search">搜索</el-button>
      </el-col>
    </el-row>
  </div>
</template>


<script>
const relations = [
    [
      {value: 1, label: '股东关系'},
      {value: 2, label: '对外投资关系'},
      {value: 3, label: '董监高关系'},
      {value: 4, label: '客户关系'},
      {value: 5, label: '供应商关系'}
    ],
    [
      {value: 'direct', label: '直接控股关联方'},
      {value: 'cor', label: '同一控制关联方'},
      {value: 'natural', label: '非控股自然人关联方'},
      {value: 'manager', label: '董监高关联方'},
      {value: 'manager_holder', label: '控股单位董监高关联方'},
      {value: 'friendly', label: ':隐式关联方'}

    ]
];

export default {
  name: "SetBar",
  data() {
    return {
      source: '',
      target: '',
      searchRelation:'',
      path: undefined,
      relationList: []
    }
  },
  mounted() {
    this.path = this.$store.state.clickPath[0]-1;
    this.relationList = relations[this.path];
    console.log(this.path);

  },
  methods: {
    search() {
      console.log("搜索");
      console.log(this.relationList);
      let input = {};
      if(this.path == 0){
        input = {'source': this.source, 'target': this.target};
      }
      else if (this.path == 1){
        input = {'source': this.source, 'order': this.searchRelation[0]};
      }
      else {
        input = {'center': this.source};
      }


      this.$emit("search",input);
    }
  }

}
</script>

<style scoped>
#SetBar{
  position: absolute;
  top: 120px;
  left: 40px;
  margin: 10px;
  width: 95%;
}
</style>