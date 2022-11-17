<template>
  <div id="Graph">
    <div id="GraphLayer" style="">
      <svg id="GraphD3"></svg>
    </div>
    <SetBar @search="findGraph"></SetBar>
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
import SetBar from "./SetBar";
import _ from "underscore";

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
const opacity = 1;
const radius = 30;

export default {
  name: "GraphD3",
  components: {SetBar},
  props:{
    isShowMainGraph: Boolean
  },
  data() {
    return {
      width: 800,
      height:600,
      zoom: null,
      path: undefined,
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
      mouse: undefined,
      mouseIsSelect: false,
      cursor: undefined,
      mouseLink: undefined,

      dialogShow: false,
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
        this.indexNew2Old = [];
        console.log(this.data);
        this.svg = d3.select("#GraphD3")
            .attr("height", this.height)
            .attr("width", this.width)
            .attr("viewBox", [-this.width / 2, -this.height / 2, this.width, this.height])
            .on("mouseleave", this.mouseLeft)
            .on("mousemove", this.mouseMoved)
            // .on("click", this.clicked);

        this.simulation = d3.forceSimulation(this.data.nodes)
            .force("charge", d3.forceManyBody().strength(-2000))
            .force("link", d3.forceLink(this.data.links).distance(radius * 10).id(function(d){return d.id;}))
            // .force("link", d3.forceLink(this.data.links).distance(radius * 10))
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

    findGraph(input){
      console.log("搜索");
      let searchData = input;
      console.log(searchData);
      this.path = this.$store.state.clickPath[0];
      let num = 0;
      if(this.path == 1) {
        num = 1;
      }
      else if(this.path == 2){
        num = 3;
      }
      else {
        num = 2;
      }
      // const url = "http://127.0.0.1:5000//fun" + num;
      const url = "http://10.249.46.195:7478/fun" + num;
      console.log(url);
      this.axios.get(url, {params: searchData})
          .then((res) => {
            console.log(res.data);
            if(res.data.nodes.length === 0 && res.data.links.length === 0) {
              console.log('没找到');
              this.dialogShow = true;
              this.$message({
                message: '未找到相关信息',
                type: 'warning'
              });
            }
            else {
              this.data = res.data;
              // this.indexNew2Old = res.data.new2old;
              // this.initialGraph();
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
    drawNodes() {
      this.node = this.node
          .data(this.data.nodes)
          .join(
              enter => enter.append("circle")
                  .attr("r", 0)
                  .attr("fill", d => colorList[d.type])
                  .attr("fill-opacity", opacity)
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
                    return d.label
                  })
                  .attr("font-size", 10)
                  .call(this.dragger),
              update => update.text(d => {
                return d.label
              }),
              exit => exit.remove()
          );
    },
    SameLinks(){
      var links = this.data.links;
      _.each(links, function(link) {
        var same = _.where(links, {
          'source': link.source,
          'target': link.target
        });

        _.each(same, function(s, i) {
          s.sameIndex = (i + 1);
          s.sameTotal = same.length;
          s.sameTotalHalf = (s.sameTotal / 2);
          s.sameUneven = ((s.sameTotal % 2) !== 0);
          s.sameMiddleLink = ((s.sameUneven === true) && (Math.ceil(s.sameTotalHalf) === s.sameIndex));
          s.sameLowerHalf = (s.sameIndex <= s.sameTotalHalf);
          s.sameArcDirection = s.sameLowerHalf ? 0 : 1;
          s.sameIndexCorrected = s.sameLowerHalf ? s.sameIndex : (s.sameIndex - Math.ceil(s.sameTotalHalf));
        });

        let sameStandard = same[0];
        let sourceStandard = sameStandard.source;
        let targetStandard = sameStandard.target;
        _.each(same,function(s){
          if(s.source === targetStandard && s.target === sourceStandard && s.sameTotal > 1){
            s.sameArcDirection = s.sameArcDirection === 0 ? 1 : 0
          }
        })
      });
      var maxSame = _.chain(links)
          .sortBy(function(x) {
            return x.sameTotal;
          })
          .last()
          .value().sameTotal;

      _.each(links, function(link) {
        link.maxSameHalf = Math.floor(maxSame / 2);
      });
      console.log(links);
    },
    drawLinks() {
      this.SameLinks();
      this.link = this.link
          .data(this.data.links)
          .join(
              enter => enter.append("path")
                  .attr("fill", "none")
                  .attr("stroke", "#999")
                  .attr("stroke-width", 2)
                  .attr("stroke-opacity", opacity)
                  .attr("marker-end", "url(#arrow)")
                  .attr("id", function(d,i){return 'link_path'+i;}),
              update => update,
              exit => exit.remove()
          );
      this.linkText = this.linkText
          .data(this.data.links)
          .join(
            enter => enter.append("text")
                .attr("text-anchor", "middle")
                .append("textPath")
                .attr("xlink:href", function(d,i){return '#link_path'+i;})
                .attr("startOffset", "50%")
                .text(d => d.description)
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

      this.link.attr("d", d => this.linkArc(d));

      this.linkText
          .attr('x', d => Math.abs(d.source.x - d.target.x) / 2)
          .attr('y', d => Math.abs(d.source.y - d.target.y) / 2)

      this.nodeText.attr('transform', d => 'translate(' + d.x + ',' + d.y + ')');

      this.cursor.attr("cx", this.cursorNode.x)
          .attr("cy", this.cursorNode.y);
    },
    linkArc(d){
      var dx = d.target.x - d.source.x + 2 * offsetX(d),
          dy = d.target.y - d.source.y + 2 * offsetY(d),
          dr = Math.sqrt(dx*dx+dy*dy) * 1.2,
          unevenCorrection = (d.sameUneven ? 0 : 0.5),
          arc = ((dr * d.maxSameHalf) / (d.sameIndexCorrected - unevenCorrection));

      if (d.sameMiddleLink) {
        arc = 0;
      }
      return "M" + (d.source.x - offsetX(d)) + " " + (d.source.y - offsetY(d)) + "A" + arc + "," + arc + " 0 0," + d.sameArcDirection + " " + (d.target.x + offsetX(d)) + "," + (d.target.y + offsetY(d));
      //   return 'M ' + (d.source.x - offsetX(d)) + ' ' + (d.source.y - offsetY(d))+' L '+ (d.target.x + offsetX(d)) +' '+ (d.target.y + offsetY(d));
      // }
      // else{
      //   var dx = d.target.x - d.source.x + 2 * offsetX(d),
      //       dy = d.target.y - d.source.y + 2 * offsetY(d),
      //       dr = Math.sqrt(dx*dx+dy*dy) * 1.2;
      //   return 'M ' + (d.source.x - offsetX(d)) + ' ' + (d.source.y - offsetY(d)) + 'A' + dr + ',' + dr + ' 0 0,1 ' + (d.target.x + offsetX(d)) + ',' + (d.target.y + offsetY(d));

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
      if(this.data.links[i].source.id === source && this.data.links[i].target.id === target){
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