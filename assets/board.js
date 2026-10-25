/* 数据寻踪——AI解码生命 · 翻页与自适应缩放（各场共用） */
var slides=[].slice.call(document.querySelectorAll(".slide")),i=0;
function go(n){if(n<0||n>=slides.length)return;slides[i].classList.remove("active");i=n;slides[i].classList.add("active");}
document.addEventListener("keydown",function(e){
  if(e.key==="ArrowRight"||e.key===" "||e.key==="PageDown")go(i+1);
  if(e.key==="ArrowLeft"||e.key==="PageUp")go(i-1);
});
document.getElementById("stage").addEventListener("click",function(e){ if(e.target.tagName!=="A") go(i+1); });
function fit(){var s=Math.min(innerWidth/1280,innerHeight/720);document.getElementById("stage").style.transform="scale("+s+")";}
addEventListener("resize",fit);fit();
