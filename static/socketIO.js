let hashmap = {};
var socket=io.connect('http://'+document.domain+':'+location.port);
socket.on('update_gauges',function(data)
{
    for(var key in data)
    {   
        var value=data[key];
        //hashmap[key]=value.split(":")[0];
        if ((value.match(/,/g) || []).length > 1)
        {
            var progressBar=document.getElementById(key);
            hashmap[key]=document.getElementById(key + "-text").innerText.split(":")[0];
            var values=value.split(',').map(Number);
            var min=values[0]; 
            var current=values[1];
            var max=values[2];
            var percentage=(current-min)/(max-min)*100;
            percentage=Math.max(0,Math.min(100,percentage));
            var progressBarColor=current<=min ? '#4caf50' : (current>=max ? '#f44336' : '#ff9800');
            progressBar.style.backgroundColor=progressBarColor;
            progressBar.style.width=percentage+'%';
            if (current<=min || current>=max)
            {
                if(current<=min)
                {
                    progressBar.style.width="100%";
                    progressBar.classList.add('blinking-progress-bar1');
                }
                else 
                {
                    progressBar.classList.add('blinking-progress-bar');
                }
            } 
            else
            {
                progressBar.classList.remove('blinking-progress-bar');
            }
            var progressText = document.getElementById(key + '-text');
            progressText.innerText = hashmap[key] + ":" + min+","+current+","+max;
        }
        else if(document.getElementById("T_"+key))
        {
            var checkbox=document.getElementById("T_"+key);
            if(value=="True")
            {
                checkbox.checked=true;
            }
            else
            {
                var switchBackground = checkbox.nextElementSibling;
                switchBackground.style.backgroundColor = '#f44336';
                checkbox.checked =false;
                switchBackground.classList.add('blinking-progress-bar');
            }
        }
        else
        {
            var element=document.getElementById(key);
            hashmap[key]=element.innerText.split(":")[0];
            element.innerText=hashmap[key]+":"+value;
        }
    }
});