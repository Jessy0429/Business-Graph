<template>
  <div id="Graph">
    <div id="GraphLayer" style="">
      <svg id="GraphD3"></svg>
    </div>
    <div id="SetBar">
      <el-row>
        <el-col :span="4">
          <el-input
                placeholder="请输入内容"
                v-model="search1Input"
                clearable>
          </el-input>
<!--          <el-autocomplete-->
<!--              class="inline-input"-->
<!--              v-model="searchInput"-->
<!--              :fetch-suggestions="searchAutoComplete"-->
<!--              placeholder="搜索"-->
<!--              @select="handleSelect"-->
<!--          >-->
<!--            <el-button slot="append" icon="el-icon-search" @click="findSubGraph"  ></el-button>-->
<!--          </el-autocomplete>-->
<!--          <el-input v-model="searchInput" clearable placeholder="搜索" @keydown.enter.native="findSubGraph">-->
<!--            <el-button slot="append" icon="el-icon-search" @click="findSubGraph"></el-button>-->
<!--          </el-input>-->
        </el-col>
        <el-col :span="2" :offset="1">
          <el-select v-model="search1Select" placeholder="选择人">
            <el-option>
            </el-option>
          </el-select>
        </el-col>
        <el-col :span="4" :offset="1">
          <el-input placeholder="请输入内容" v-model="search2Input" clearable></el-input>
        </el-col>
        <el-col :span="2" :offset="1">
          <el-select v-model="search2Select" placeholder="选择人"></el-select>
        </el-col>
        <el-col :span="4" :offset="1">
          <el-select v-model="searchRelation" multiple placeholder="选择关系">
            <el-option
                v-for="item in relationlist"
                :key="item.value"
                :label="item.label"
                :value="item.value">
            </el-option>
          </el-select>
        </el-col>
        <el-col :span="1" :offset="1">
          <el-button type="primary" round @click="findSubGraph">搜索</el-button>
        </el-col>

      </el-row>
    </div>
    <div id="Tags">
      <el-tag :color="nodeLables[0].color" effect="dark">{{nodeLables[0].label}}</el-tag>
      <el-tag :color="nodeLables[1].color" effect="dark">{{nodeLables[1].label}}</el-tag>
      <el-tag :color="nodeLables[2].color" effect="dark">{{nodeLables[2].label}}</el-tag>
      <el-tag :color="nodeLables[3].color" effect="dark">{{nodeLables[3].label}}</el-tag>
    </div>

  </div>
</template>

<script>
import * as d3 from 'd3';

// var nodes = [
//   {index: 0, label: 'Node 2', type: 1},
//   {index: 1, label: 'Node 3', type: 2},
//   {index: 2, label: 'Node 4', type: 3}];
// var edges = [{source: 0, target: 2},
//   {source: 0, target: 1}];

const colorList = [
  '#FCFE8B',
  '#B9F385',
  '#75D6C9',
  '#BC7CDA',
  '#F385A8',
];
const relations = [
  {value: 1, label: '股东关系'},
  {value: 2, label: '对外投资关系'},
  {value: 3, label: '董监高关系'},
  {value: 4, label: '客户关系'},
  {value: 5, label: '供应商关系'}
];
const opacity = 1;
const radius = 30;

export default {
  name: "GraphD3",
  components: {},
  props:{
    isShowMainGraph: Boolean
  },
  data() {
    return {
      width: 800,
      height:600,
      zoom: null,
      isFullScreen: false,
      isVisible: false,
      timer: false,
      search1Input: '',
      search1Select: '',
      search2Input: '',
      search2Select: '',
      searchRelation:'',
      autoCompleteList: [],
      selectAutoComplete: {},
      isRecommendQuery: false,
      cardTitle: '',
      cardItems: [],
      indexNew2Old: [],

      data: {},
      // data: {}
      // data: {nodes: nodes, links: edges},

      nodeLables : [
        { color: colorList[1], label: '自然人' },
        { color: colorList[2], label: '上市公司' },
        { color: colorList[3], label: '非上市公司' },
        { color: colorList[4], label: '搜索的公司' }
      ],
      node: undefined,
      link: undefined,
      arrow: undefined,
      relationlist: relations,
      mouse: undefined,
      mouseIsSelect: false,
      cursor: undefined,
      mouseLink: undefined,

      isShown: false,
      selectedNode: {},
      selectedEdge: {},
      cursorNode: {},

      svg: {},
      simulation: {},
      dragger: {},
    }
  },
  mounted() {
  //解决esc键无法触发事件
    let that = this;
    this.setGraphWindow();
    window.onresize = function(){
      if(!that.timer){ // 使用节流机制，降低函数被触发的频率
        that.timer = true;
        setTimeout(function(){
          that.setGraphWindow();
          that.timer = false;
        },400)
      }
    };

    this.initialGraph();
  },
  watch:{
    isShowMainGraph: function (newFlag, oldFlag){
      if(newFlag) {
        this.showMainGraph()
      }
    }
  },
  methods:{
    // 初始化图
    initialGraph(){
      const url = "http://127.0.0.1:5000/api/get_data";
      this.axios.get(url)
          .then((res) => {
            this.data = res.data;
            // this.data = {"nodes":[
            //   {index: 0, label: 'Node 2', type: 1},
            //   {index: 1, label: 'Node 3', type: 2},
            //   {index: 2, label: 'Node 4', type: 3}],
            //     "edges":[{source: 0, target: 2},
            //   {source: 0, target: 1}]};
            this.indexNew2Old = [];
            console.log(res.data);
            this.svg = d3.select("#GraphD3")
                .attr("height", this.height)
                .attr("width", this.width)
                .attr("viewBox", [-this.width / 2, -this.height / 2, this.width, this.height])
                .on("mouseleave", this.mouseLeft)
                .on("mousemove", this.mouseMoved)
                // .on("click", this.clicked);

            this.simulation = d3.forceSimulation(this.data.nodes)
                .force("charge", d3.forceManyBody().strength(-2000))
                .force("link", d3.forceLink(this.data.links).distance(radius * 10))
                .force('collide', d3.forceCollide().radius(radius))
                .force("x", d3.forceX())
                .force("y", d3.forceY())
                .on("tick", this.ticked);

            this.cursor = this.svg.append('g')
                .append("circle")
                .attr("display","none")
                .attr("fill", "none")
                .attr("stroke-width", 2)
                .attr("r", radius);
            this.link = this.svg.append("g")
                .selectAll("path");
            this.linkText= this.svg.append("g")
                .selectAll("text")
            this.mouseLink = this.svg.append("g")
                .selectAll("line");
            this.node = this.svg.append("g")
                .selectAll("circle");
            this.nodeText = this.svg.append("g")
                .selectAll("text");
            this.svg.append("defs").append("marker")
                .attr("id", "arrow")
                .attr("markerUnits","userSpaceOnUse")
                .attr("viewBox", "0 0 12 12")
                .attr("refX", 10)
                .attr("refY", 6)
                .attr("markerWidth", 26)//标识的大小
                .attr("markerHeight", 26)
                .attr("orient", "auto")//绘制方向，可设定为：auto（自动确认方向）和 角度值
                .attr("stroke-width",2)//箭头宽度
                .append("path")
                .attr("d", "M2,2 L10,6 L2,10 L6,6 L2,2")//箭头的路径
                .attr('fill',"#666");//箭头颜色

            this.dragger = this.drag(this, this.simulation, this.mouseLink, this.data);
            this.zoom = d3.zoom().extent([[0, 0], [this.width, this.height]]).scaleExtent([0.1, 4]).on("zoom", this.zoomed);
            this.svg.call(this.zoom);
            this.svg.on("dblclick.zoom",null);
            
            this.updateGraph();
          })
          .catch((error) => {
            console.log(error);
          })
    },

    setGraphWindow() {
      this.height = window.innerHeight-80;
      this.width = window.innerWidth-200;
      // console.log(this.height, this.width);
      this.svg = d3.select("#GraphD3")
          .attr("height", this.height)
          .attr("width", this.width)
          .attr("viewBox", [-this.width / 2, -this.height / 2, this.width, this.height])
    },

    // 鼠标事件
    mouseLeft() {
      this.mouse = null;
    },
    mouseMoved(event) {
      const [x, y] = d3.pointer(event);
      this.mouse = {x, y};
      // this.simulation.alpha(0.3).restart();
    },

    getSubGraph(){
      const url = "http://127.0.0.1:5000/api/get_subGraphData";
      this.axios.get(url, {params: {baseNodeIndex: this.selectedNode.index, numLayer: 3}})
          .then((res) => {
            this.mouseLeaveNode();
            console.log(res.data);
            this.data = res.data.subgraph;
            this.indexNew2Old = res.data.new2old;
            this.updateGraph();
          })
          .catch((error) =>{
            console.log(error)
          })
    },

    findSubGraph(){
      console.log("搜索");
      let search = {'search1':this.search1Input, 'search2':this.search2Input};
      console.log(search);
      const url = "http://127.0.0.1:5000/api/get_search";
      this.axios.get(url, {params: {search: search}})
          .then((res) => {
            console.log(res.data);
            if(res.data == false) {
              this.$message({
                message: '未找到相关信息',
                type: 'warning'
              });
            }
            else {
              this.data = res.data.graph;
              this.indexNew2Old = res.data.new2old;
              this.updateGraph();
              // if (this.isInList(this.searchInput, this.autoCompleteList)){
              //   this.dialogCardVisible = true
              //   this.cardTitle = this.searchInput
              //   this.cardItems = this.data.nodes.slice(1)
              // }
            }
          })
          .catch((error) =>{
            console.log(error)
          })


    },

    searchAutoComplete(queryString, cb){
      // console.log(queryString)

      if (!this.isInList(queryString, this.autoCompleteList)){
        this.isRecommendQuery = false
        const url = "http://127.0.0.1:5000/api/get_autoComplete";
        this.axios.get(url, {params: {search: this.searchInput}})
            .then((res) => {
              // console.log(res.data);
              // this.data = res.data;
              this.autoCompleteList = res.data;
              cb(res.data);
            })
            .catch((error) =>{
              console.log(error);
            })
      }
      else {
        cb([]);
      }
    },

    handleSelect() {
      this.isRecommendQuery = true;
    },

    isInList(value, list){
      for(let i=0; i < list.length; i++){
        if(value === list[i]['value']){
          return true;
        }
      }
      return false;
    },


    showMainGraph(){
      // console.log(this.isShowMainGraph, this.$store.state.showMainGraph)
      const url = "http://127.0.0.1:5000/api/get_mainGraphData";
      this.axios.get(url)
          .then((res) => {
            console.log(res.data);
            this.data = res.data;
            this.indexNew2Old = [];
            this.updateGraph();

          })
          .catch((error) =>{
            console.log(error)
          })
    },
    drawNodes() {
      this.node = this.node
          .data(this.data.nodes)
          .join(
              enter => enter.append("circle")
                  .attr("r", 0)
                  .attr("fill", d => colorList[d.type])
                  .attr("fill-opacity", opacity)
                  .attr("index", d => d.index)
                  .call(enter => enter.transition().attr("r", radius))
                  .call(this.dragger),
              update => update
                  .attr("fill", d => colorList[d.type]),
                  // .attr("r", d => d.radius),
              exit => exit.remove()
          );
      this.drawNodeText();
    },
    drawNodeText() {
      this.nodeText = this.nodeText
          .data(this.data.nodes)
          .join(
              enter => enter.append("text")
                  .attr("index", d => d.index)
                  .attr("text-anchor","middle")
                  .text(d => {
                    if (d.label.length >= 7) {
                      // return d.label
                      return d.label.substr(0, 4) + '…'
                    }
                    else {
                      return d.label
                    }
                  })
                  .call(this.dragger),
              update => update.text(d => {
                if (d.label.length >= 4) {
                  return d.label.substr(0, 4) + '…'
                }
                else {
                  return d.label
                }
              }),
              exit => exit.remove()
          );
    },

    drawLinks() {
      this.link = this.link
          .data(this.data.links)
          .join(
              enter => enter.append("path")
                  .attr("fill", "none")
                  .attr("stroke", "#999")
                  .attr("stroke-width", 2)
                  .attr("stroke-opacity", opacity)
                  .attr("marker-end", "url(#arrow)")
                  .attr("index", d => d.index)
                  .attr("id", d => "link_path_"+d.index)
                  .on("mouseenter", d => this.mouseEnterEdge(d))
                  .on("mouseleave",d => this.mouseLeaveEdge(d)),
              update => update,
              exit => exit.remove()
          );
      this.linkText = this.linkText
          .data(this.data.links)
          .join(
            enter => enter.append("text")
                .attr("text-anchor", "middle")
                .append("textPath")
                .attr("xlink:href", d => "#link_path_"+d.index)
                .attr("startOffset", "50%")
                .text(d => d.label)
                .attr("fill", "#999")
                .attr("font-size", 15)
                .call(this.dragger),
            update => update,
            exit => exit.remove()
          );
    },

    // 更新图
    updateGraph() {
      this.drawLinks();

      this.drawNodes();


      this.simulation.nodes(this.data.nodes);
      this.simulation.force("link").links(this.data.links);
      this.simulation.alpha(1).restart();
    },

    ticked() {
      this.node.attr("cx", d => d.x)
          .attr("cy", d => d.y);

      this.link.attr("d", d => this.linkArc(d))

      this.linkText
          .attr('x', d => Math.abs(d.source.x - d.target.x) / 2)
          .attr('y', d => Math.abs(d.source.y - d.target.y) / 2)

      this.nodeText.attr('transform', d => 'translate(' + d.x + ',' + d.y + ')');

      this.cursor.attr("cx", this.cursorNode.x)
          .attr("cy", this.cursorNode.y);
    },
    linkArc(d){
      if(this.linkNotExist(d.source.index, d.target.index) || this.linkNotExist(d.target.index, d.source.index)) {
        return 'M ' + (d.source.x - offsetX(d)) + ' ' + (d.source.y - offsetY(d))+' L '+ (d.target.x + offsetX(d)) +' '+ (d.target.y + offsetY(d));
      }
      else{
        var dx = d.target.x - d.source.x + 2 * offsetX(d),
            dy = d.target.y - d.source.y + 2 * offsetY(d),
            dr = Math.sqrt(dx*dx+dy*dy) * 1.2;
        return 'M ' + (d.source.x - offsetX(d)) + ' ' + (d.source.y - offsetY(d)) + 'A' + dr + ',' + dr + ' 0 0,1 ' + (d.target.x + offsetX(d)) + ',' + (d.target.y + offsetY(d));
      }

      function offsetX(d){
        return radius * (d.source.x - d.target.x) / Math.hypot(d.source.x-d.target.x, d.source.y-d.target.y)
      }
      function offsetY(d){
        return radius * (d.source.y - d.target.y) / Math.hypot(d.source.x-d.target.x, d.source.y-d.target.y)
      }
    },

    drag(self) {
      let targetNodes = [];
      function dragStarted(event) {
        // console.log(event);
        if (!event.active) self.simulation.alphaTarget(0.3).restart();
        event.subject.fx = event.subject.x;
        event.subject.fy = event.subject.y;
      }

      function dragged(event) {
        // console.log(event);
        event.subject.fx = event.x;
        event.subject.fy = event.y;
      }

      function dragEnded(event) {
        if (!event.active) self.simulation.alphaTarget(0);
        event.subject.fx = null;
        event.subject.fy = null;

      }

      return d3.drag()
          .on("start", dragStarted)
          .on("drag", dragged)
          .on("end", dragEnded);
    },

    linkNotExist(source, target){
    // console.log(source, target);
    let notExist = true;
    for(let i = 0, len=this.data.links.length; i < len; i++) {
      if(this.data.links[i].source.index === source && this.data.links[i].target.index === target){
        notExist = false;
      }
    }
    return notExist;
    },

    //编辑视图相关
    zoomed({transform}) {
      d3.selectAll("g").attr("transform", transform);
     }
  },

}
</script>

<style scoped>
  /*#GraphD3{*/
  /*  width: 800px;*/
  /*  height: 600px;*/
  /*}*/
  #GraphLayer{
    z-index: 1;
    /*border:6px solid #2196F3;*/
    /*background-color: #ddffff;*/
  }
  #SetBar{
    position: absolute;
    top: 120px;
    left: 40px;
    margin: 10px;
    width: 95%;
  }
  .text {
    font-size: 15px;
  }
  .item {
    padding: 10px 0;
  }
  #Tags{
    position: relative;
    top: -230px;
    left: 10px;
    height: 150px;
    width: 100px;
    display:table-cell;
    /*inline-height: 150px;*/
  }
  .el-tag{
    display: inline-block;
    vertical-align: middle;
    margin: 5px;
  }

</style>