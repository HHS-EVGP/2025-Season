class odometer {
    /*
    Odometer code comes from:
    That Guy | 2019
    https://www.youtube.com/watch?v=JNqlavrjvDg
    */
    constructor(x,y,title,size=1,rate,max=100,min=0,red=3) {
        this.x = x;            // X Location
        this.y = y;            // Y Location
        this.rate = rate;      // Rate (Relates to the value)
        this.min = min;        // Minimum Value
        this.max = max;        // Maximum Value
        this.red = red;        // Number of Red Numbers (From Right)
        this.size = size*200;  // Size of Odometer
        this.title = title;    // Name of Odometer
    }
    setup(){
        strokeWeight(0);
        fill('#5D6D7E');
        circle(this.x, this.y, this.size);
        fill('#D6DBDF');    
        arc(this.x, this.y, this.size, this.size, PI - QUARTER_PI , QUARTER_PI);
        fill('#5D6D7E'); 
        circle(this.x, this.y, this.size*0.9);
        textSize(this.size*0.075);
        fill('#17202A'); 
        text( "__" + this.rate, this.x, this.y - this.size*0.1);
        textSize(this.size*0.125);
        text( this.title, this.x, this.y+this.size*0.05);
        textSize(this.size*0.075);
        let x_table = [
            -0.265165042945,
            -0.356646193611,
            -0.370383127723,
            -0.303381372891,
            -0.170246437402,
            0.0,
            0.170246437402,
            0.303381372891,
            0.370383127723,
            0.356646193611,
            0.265165042945
        ]
        let y_table = [
            0.265165042945,
            0.115881372891,
            -0.0586629243901,
            -0.22041946961,
            -0.334127446571,
            -0.375,
            -0.334127446571,
            -0.22041946961,
            -0.0586629243901,
            0.115881372891,
            0.265165042945
        ]
        fill('white');
        for (let i = 0; i < 11-this.red; i++) {
            text(round((i*(this.max-this.min)/10)+this.min), this.x+this.size*(x_table[i]), this.y+this.size*(y_table[i]));
        }
        fill('red');
        for (let i = 11-this.red; i < 11; i++) {
            text(round((i*(this.max-this.min)/10)+this.min), this.x+this.size*(x_table[i]), this.y+this.size*(y_table[i]));
        }
    }
    draw(value) {
        strokeWeight(0);
        fill('#5D6D7E');
        circle(this.x, this.y, this.size);
        this.value = value;
        fill('#D6DBDF');    
        arc(this.x, this.y, this.size, this.size, PI - QUARTER_PI , QUARTER_PI);
        fill('#17202A');
        arc(this.x, this.y, this.size, this.size, PI-QUARTER_PI, PI-QUARTER_PI + (((270/(this.max-this.min))*(this.value-this.min))*PI/180));
        fill('#5D6D7E'); 
        circle(this.x, this.y, this.size*0.9);
        textSize(this.size*0.075);
        fill('#17202A'); 
        text( this.value + this.rate, this.x, this.y - this.size*0.1);
        textSize(this.size*0.125);
        text( this.title, this.x, this.y+this.size*0.05);
        textSize(this.size*0.075);
        let x_table = [
            -0.265165042945,
            -0.356646193611,
            -0.370383127723,
            -0.303381372891,
            -0.170246437402,
            0.0,
            0.170246437402,
            0.303381372891,
            0.370383127723,
            0.356646193611,
            0.265165042945
        ]
        let y_table = [
            0.265165042945,
            0.115881372891,
            -0.0586629243901,
            -0.22041946961,
            -0.334127446571,
            -0.375,
            -0.334127446571,
            -0.22041946961,
            -0.0586629243901,
            0.115881372891,
            0.265165042945
        ]
        fill('white');
        for (let i = 0; i < 11-this.red; i++) {
            text(round((i*(this.max-this.min)/10)+this.min), this.x+this.size*(x_table[i]), this.y+this.size*(y_table[i]));
        }
        fill('red');
        for (let i = 11-this.red; i < 11; i++) {
            text(round((i*(this.max-this.min)/10)+this.min), this.x+this.size*(x_table[i]), this.y+this.size*(y_table[i]));
        }
        fill('#C0392B');
        let angle = (((270/(this.max-this.min))*(this.value-this.min))-135)*PI/180;
        let x = this.x + this.size*0.45 * sin(angle);
        let y = this.y - this.size*0.45 * cos(angle);
        let y1 = this.y - this.size*0.3 * cos(angle) + this.size*0.025 * sin(angle);
        let x1 = this.x + this.size*0.3 * sin(angle) + this.size*0.025 * cos(angle);
        let y2 = this.y - this.size*0.3 * cos(angle) - this.size*0.025 * sin(angle);
        let x2 = this.x + this.size*0.3 * sin(angle) - this.size*0.025 * cos(angle);
        triangle(x, y, x1, y1, x2, y2);
    }
    hide(){
        strokeWeight(0);
        fill('white'); 
        circle(this.x, this.y, this.size*1.01);
    }
}

class odometer_counter {
    constructor(x,y,title,size=1) {
        this.x = x;            // X Location
        this.y = y;            // Rate (Relates to the value)
        this.size = size*200;  // Size of Odometer
        this.title = title;    // Name of Odometer
    }
    setup(){
        textAlign(CENTER,CENTER);

        var value = 0;
        fill("white");
        rect(
            this.x-this.size,
            this.y-(this.size/2.8),
            this.size*2,
            this.size*0.125
        );
        fill("#5D6D7E");
        rect(
            this.x-this.size,
            this.y-(this.size/2)+(this.size/4),
            (this.size*2),
            (this.size/2)
        );
        fill("#D6DBDF");
        for (let i = 0; i < 6; i++) {
            rect(
                this.x-this.size+i*3*(this.size*2)/19+(i+1)*(this.size*2)/(19*7),
                this.y-(this.size/2)+(this.size*2)/(19*7)+(this.size/4),
                3*(this.size*2)/19,
                (this.size/2)-2*(this.size*2)/(19*7)
            );
        }
        fill("#17202A");
        textSize((this.size/2)-(this.size/100));
        let strNum = value.toFixed(3);
        let parts = strNum.replace('.', '').split('');
        let result = parts.map(digit => parseInt(digit, 10));
        while (result.length < 6) {
            result.unshift(0);
        }
        let numbers = [];
        numbers = result;
        for (let i = 0; i < 6; i++) {
            text(
                numbers[i],
                this.x-5*(this.size*2)/12+i*(this.size*2)/6,
                this.y+(this.size/30)
            );
        };
        fill("red");
        text(
            ".",
            this.x,
            this.y+(this.size/30)
        );
        textSize(this.size*0.125);
        fill("#17202A");
        text(
            this.title,
            this.x,
            this.y-(this.size/3.4)
        );
    }
    draw(value) {
        textAlign(CENTER,CENTER);

        value = round(value, 3);
        fill("white");
        rect(
            this.x-this.size,
            this.y-(this.size/2.8),
            this.size*2,
            this.size*0.125
        );
        fill("#5D6D7E");
        rect(
            this.x-this.size,
            this.y-(this.size/2)+(this.size/4),
            (this.size*2),
            (this.size/2)
        );
        fill("#D6DBDF");
        for (let i = 0; i < 6; i++) {
            rect(
                this.x-this.size+i*3*(this.size*2)/19+(i+1)*(this.size*2)/(19*7),
                this.y-(this.size/2)+(this.size*2)/(19*7)+(this.size/4),
                3*(this.size*2)/19,
                (this.size/2)-2*(this.size*2)/(19*7)
            );
        }
        fill("#17202A");
        textSize((this.size/2)-(this.size/100));
        let strNum = value.toFixed(3);
        let parts = strNum.replace('.', '').split('');
        let result = parts.map(digit => parseInt(digit, 10));
        while (result.length < 6) {
            result.unshift(0);
        }
        let numbers = [];
        numbers = result;
        for (let i = 0; i < 6; i++) {
            text(
                numbers[i],
                this.x-5*(this.size*2)/12+i*(this.size*2)/6,
                this.y+(this.size/30)
            );
        };
        fill("red");
        text(
            ".",
            this.x,
            this.y+(this.size/30)
        );
        textSize(this.size*0.125);
        fill("#17202A");
        text(
            this.title,
            this.x,
            this.y-(this.size/3.4)
        );
    }
    hide(){
        strokeWeight(0);
        fill("white");
        rect(
            this.x-this.size*1.01,
            this.y-this.size/2.8-1,
            this.size*2.02,
            this.size*0.615+1
        );
    }
}

class graph {
    constructor(x,y,title,size=1,x_axis_title="Counter",y_axis_title="Value",unit="") {
        this.x = x;            // X Location
        this.y = y;            // Y Location
        this.size = size*200;
        this.title = title;
        this.x_title = x_axis_title;
        this.y_title = y_axis_title;
        this.unit = unit;
    }
    setup(){
        strokeWeight(0);
        fill("#dbdbdb");
        rect(this.x-this.size/2,this.y,this.size,this.size*3/4);
        strokeWeight(1);
        fill("black");
        line(
            this.x-this.size/2+(11/64)*this.size,
            this.y+this.size*(3/4)*(7/8),
            this.x+this.size/2,
            this.y+this.size*(3/4)*(7/8)
        );
        line(
            this.x-this.size/2+(11/64)*this.size,
            this.y,
            this.x-this.size/2+(11/64)*this.size,
            this.y+this.size*(3/4)*(7/8)
        );
        
        textSize(10*this.size/200);
        text(
            this.x_title,
            this.x,
            this.y+this.size*(3/4)-4*this.size/200
        );
        let list_of_y_axis = [];
        for (let i = 0; i < this.y_title.length; i++) {
            list_of_y_axis[i] = (this.y_title)[i];
            if(this.y_title.length%2 == 1){
                text(
                    list_of_y_axis[i],
                    this.x-this.size/2+5*this.size/200,
                    this.y+this.size*(3/4)*(1/2)+(9*this.size/200)*(i-(this.y_title.length-1)/2)
                );
            }else{
                text(
                    list_of_y_axis[i],
                    this.x-this.size/2+5*this.size/200,
                    this.y+this.size*(3/4)*(1/2)+(9*this.size/200)*(i-(this.y_title.length)/2)
                );
            }
        }
        text(
            this.title,
            this.x,
            this.y+6*this.size/200
        );
    }
    draw(x_values,y_values){
        this.setup();

        let leng = x_values.length;
        let y_min = min(y_values);
        let y_max = max(y_values);

        console.log(y_min)

        for (let i = 0; i < leng; i++) {
            let x_point = (this.x-this.size/2+(1/8)*this.size) + (((i+0.5)/leng)*((this.x+this.size/2-(6*this.size/200))-(this.x-this.size/2+(1/8)*this.size)) + (2.5/64*this.size));
            let x_point3 = (this.x-this.size/2+(1/8)*this.size) + ((((i+1)+0.5)/leng)*((this.x+this.size/2-(6*this.size/200))-(this.x-this.size/2+(1/8)*this.size)) + (2.5/64*this.size));
            let y_point = (this.y+(18*this.size/200)) + (i/10*((this.y+this.size*(3/4)*(7/8)-(6*this.size/200))-(this.y+(18*this.size/200))));
            let y_point2 = map(
                y_values[i],
                y_min,
                y_max,
                (this.y+(18*this.size/200)) + ((leng-1)/10*((this.y+this.size*(3/4)*(7/8)-(6*this.size/200))-(this.y+(18*this.size/200)))),
                (this.y+(18*this.size/200)) + (0/10*((this.y+this.size*(3/4)*(7/8)-(6*this.size/200))-(this.y+(18*this.size/200))))
                );
            let y_point3 = map(
                y_values[i+1],
                y_min,
                y_max,
                (this.y+(18*this.size/200)) + ((leng-1)/10*((this.y+this.size*(3/4)*(7/8)-(6*this.size/200))-(this.y+(18*this.size/200)))),
                (this.y+(18*this.size/200)) + (0/10*((this.y+this.size*(3/4)*(7/8)-(6*this.size/200))-(this.y+(18*this.size/200))))
                );
            //X
            text(
                x_values[i],
                x_point,
                this.y+this.size*(3/4)*(7/8)+(6*this.size/200)
            );
            textAlign(RIGHT, CENTER);
            text(
                round(y_min+(y_max-y_min)*(map(i,0,(leng-1),1,0)),1),
                this.x-this.size/2+(11/64)*this.size - (1*this.size/200),
                y_point
            );
            textAlign(CENTER, CENTER);
            strokeWeight(3);
            point(
                x_point,
                y_point2
            );
            strokeWeight(1);
            line(
                x_point,
                y_point2,
                x_point3,
                y_point3
            );
        }
    }
    hide(){
        strokeWeight(0);
        fill("white");
        rect(this.x-this.size/2,this.y,this.size,this.size*3/4)
    }
}

class throttle {
    constructor(x,y,title,size) {
        this.x = x;            // X Location
        this.y = y;            // Y Location
        this.size = size*200;      // Size
        this.title = title;    // Name
    }
    setup(){
        /* 
        Gradient Code comes from: 
        Jeff Thompson | 2021 | jeffreythompson.org
        https://editor.p5js.org/jeffThompson/sketches/ta7msUszJ
        */
        let gradient = drawingContext.createLinearGradient(this.x,this.y, this.x+this.size,this.y);
        gradient.addColorStop(0, 'green');
        gradient.addColorStop(0.35, 'green');
        gradient.addColorStop(0.55, 'yellow');
        gradient.addColorStop(0.75, 'orange');
        gradient.addColorStop(1, 'red');
        drawingContext.fillStyle = gradient;
        strokeWeight(0);
        triangle(
            this.x,this.y,
            this.x+this.size,this.y,
            this.x+this.size,this.y-this.size*(3/8)
        );
        strokeWeight(1);
        line(this.x,this.y,this.x+this.size,this.y);
        line(this.x,this.y,this.x+this.size,this.y-this.size*(3/8));
        line(this.x+this.size,this.y-this.size*(3/8),this.x+this.size,this.y);

        translate(this.x,this.y-this.size*(1/16));
        rotate(-0.35877);
        textSize(this.size/10)
        fill("black");
        text(this.title,this.size/2,0);
        rotate(0.35877);
        translate(-this.x,-this.y+this.size*(1/16));

        drawingContext.fillStyle = "white";
    }
    draw(value){
        this.setup();

        fill("white");
        stroke("white");
        strokeWeight(1);

        rect(
            this.x+this.size*(value),
            this.y-this.size*(3/8),
            this.size*(1-value)+1,
            this.size*(3/8)+1
        );

        stroke("black");
        strokeWeight(1);
        line(this.x,this.y,this.x+this.size,this.y);
        line(this.x,this.y,this.x+this.size,this.y-this.size*(3/8));
        line(this.x+this.size,this.y-this.size*(3/8),this.x+this.size,this.y);
    }
    hide(){
        fill("white");
        stroke("white");
        strokeWeight(1);
        rect(
            this.x,
            this.y-this.size*(3/8),
            this.size+1,
            this.size*(3/8)+1
        );
    }
}

class brake {
    constructor(x,y,title,size) {
        this.x = x;            // X Location
        this.y = y;            // Y Location
        this.size = size*200;      // Size
        this.title = title;    // Name
    }
    setup(){
        /* 
        Gradient Code comes from: 
        Jeff Thompson | 2021 | jeffreythompson.org
        https://editor.p5js.org/jeffThompson/sketches/ta7msUszJ
        */
        let gradient = drawingContext.createLinearGradient(this.x,this.y, this.x+this.size,this.y);
        gradient.addColorStop(0, 'black');
        gradient.addColorStop(0.25, 'black');
        gradient.addColorStop(0.45, 'black');
        gradient.addColorStop(0.75, 'red');
        gradient.addColorStop(1, 'red');
        drawingContext.fillStyle = gradient;
        strokeWeight(0);
        triangle(
            this.x,this.y,
            this.x+this.size,this.y,
            this.x+this.size,this.y-this.size*(3/8)
        );
        strokeWeight(1);
        line(this.x,this.y,this.x+this.size,this.y);
        line(this.x,this.y,this.x+this.size,this.y-this.size*(3/8));
        line(this.x+this.size,this.y-this.size*(3/8),this.x+this.size,this.y);

        translate(this.x,this.y-this.size*(1/16));
        rotate(-0.35877);
        textSize(this.size/10)
        fill("black");
        text(this.title,this.size/2,0);
        rotate(0.35877);
        translate(-this.x,-this.y+this.size*(1/16));

        drawingContext.fillStyle = "white";
    }
    draw(value){
        this.setup();

        fill("white");
        stroke("white");
        strokeWeight(1);

        rect(
            this.x+this.size*(value),
            this.y-this.size*(3/8),
            this.size*(1-value)+1,
            this.size*(3/8)+1
        );

        stroke("black");
        strokeWeight(1);
        line(this.x,this.y,this.x+this.size,this.y);
        line(this.x,this.y,this.x+this.size,this.y-this.size*(3/8));
        line(this.x+this.size,this.y-this.size*(3/8),this.x+this.size,this.y);
    }
    hide(){
        fill("white");
        stroke("white");
        strokeWeight(1);
        rect(
            this.x,
            this.y-this.size*(3/8),
            this.size+1,
            this.size*(3/8)+1
        );
    }
}

class plain_text {
    constructor(x,y,title,size) {
        this.x = x;            // X Location
        this.y = y;            // Y Location
        this.title = title;    // Name
        this.size = size;
    }
    setup(){
        fill("lightgray");
        strokeWeight(1);
        rect(
            this.x,this.y,
            300*this.size,50*this.size
        );
        fill("black");
        strokeWeight(1);
        textSize(17*this.size);
        textAlign(CENTER,TOP);

        text(
            this.title+":",
            this.x+150*this.size,
            this.y+2*this.size
        );
    }
    draw(value){
        this.setup();
        textSize(19*this.size);
        textAlign(CENTER,BOTTOM);
        text(
            value,
            this.x+150*this.size,
            this.y+45*this.size
        );
    }
    hide(){
        fill("white");
        strokeWeight(2);
        stroke("white");
        rect(
            this.x,this.y,
            300*this.size,50*this.size
        );
        strokeWeight(1);
        stroke("black");

    }
}

class blank {
    constructor(x,y,title) {
        this.x = x;            // X Location
        this.y = y;            // Y Location
        this.title = title;    // Name
    }
    setup(){

    }
    draw(value){

    }
    hide(){
        
    }
}