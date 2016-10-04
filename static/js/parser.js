
function parser(data){
	var width ;
	var height ;
	
	//椭圆弧的半轴长
	var macroaxis=5;
	var minoraxis=3;
	
	var space=50;
	
	data.unshift({"id": -1, 
				"cont": "Root", })	;  
				
				
	 data.forEach(function(x,y){
			x.x=y*60+space;
			x.y=0;
			width=x.x;
			
	 });	

	width=width+space/2;
	 
	height=width/(macroaxis*2)*minoraxis+space+10 ;
	
	data.forEach(function(x,y){
			x.y=height-10;
	 });	
	
	
	data.forEach(function(x,y){
		data.forEach(function(item,i){
			if(x.parent== item.id)
			{
				//指向时可以做一些调整 指出去+1 被指-1...
				var aim ={x:x.x,y:x.y-space};
				var start ={x:item.x,y:item.y-space};
				var dir =1//1为顺指针 0为逆时针
				if (x.id<item.id)
				{
					start.x-=space/4;
					 dir =0;
				}else
					start.x+=space/4;
					
				x.curve_path = "M"+start.x+","+start.y+
				" A"+macroaxis+","+minoraxis+" 0 1,"
				+dir+" "+aim.x+","+aim.y;
				
				//计算文字标签的坐标
				x.tagX=(start.x+aim.x)/2
				x.tagY=start.y-Math.abs(start.x-aim.x)/(macroaxis*2)*minoraxis;
				
				console.log(x);
			}
		
		});
		

	});

	var correct_factor=d3.min(data,function(d){console.log(d);  return d.tagY;});
		correct_factor=space-correct_factor

		height=height+correct_factor;
	var svg = d3.select("#parserTree");
				

	/*SVG的<defs>元素用于预定义一个元素使其能够在SVG图像中重复使用。
	例如你可以将一些图形制作为一个组，并用<defs>元素来定义它，然后
	你就可以在SVG图像中将它当做简单图形来重复使用。*/

	//创建箭头
	var defs = svg.append("defs");

	var arrowMarker = defs.append ("marker")
							.attr("id","arrow")
							.attr("markerUnits","strokeWidth")
							.attr("markerWidth","9")
							.attr("markerHeight","9")
							.attr("viewBox","0 0 12 12")
							//refX refY在 viewBox 内的基准点，绘制时此点在直线端点上
							.attr("refX","6")
							.attr("refY",6)
							.attr("orient","auto");
	//画出箭头的样子
	var arrow_path = "M2,2 L10,6 L2,10 L6,6 L2,2";
						
	arrowMarker.append("path")
			.attr("d",arrow_path)
			.attr("fill","blue");
		
	var curve = svg.selectAll(".curve")
				.data(data)
				.enter()
				.append("path")
				.attr("d",function(d,i){ 
				
				return d.curve_path;})
				//在曲线所围的区域的填充色
				.attr("fill","none")
				.attr("stroke","red")
				.attr("stroke-width",2)
				.attr("marker-end","url(#arrow)")
				.attr("class","curve")
				.attr("transform", "translate(" + 0 + "," + correct_factor + ")");			
		
			

	var tag = svg.selectAll(".tag")
				.data(data)
				.enter().append("text")
				.attr("class","tag")
				.attr("x",function(d){return d.tagX;})
				.attr("y",function(d){
					d.tagY=d.tagY+correct_factor;
					return d.tagY;})
				.attr("text-anchor", "middle")
				.text(function(d){return d.relate;});		

			
			svg.append("g")
				.selectAll("text")
				.data(data)
				.enter()
				.append("text")
				.attr("x",function(d){return d.x;})
				.attr("y",function(d){
					d.y=d.y+correct_factor;
					height=d.y+space;
					return d.y;})
				.attr("text-anchor", "middle")
				.text(function(d, i){
				return d.cont;})
				.on("mouseover",function(d){
					tag.style("fill-opacity",function(tag){
						if( tag.id != d.id && tag.parent != d.id )
							return 0;
						});
					curve.style("opacity",function(curve){
						if( curve.id != d.id && curve.parent != d.id )
							return 0;
						});	
						})
				.on("mouseout",function(d){
					tag.style("fill-opacity",function(tag){
						if( tag.id != d.id && tag.parent != d.id )
							return 1;
						});
					curve.style("opacity",function(curve){
						if( curve.id != d.id && curve.parent != d.id )
							return 1;
						});	
						});
										
			svg.attr("width",width)
				.attr("height",height);
	

}













