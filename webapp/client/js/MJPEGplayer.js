export default class MJPEGplayer{
    constructor(canvas, {
        width,
        height
    }) {
        if(!width) throw "Need to supply width";
        if(!height) throw "Need to supply height";

        canvas.width  = width;
        canvas.height = height;

        let ctx = canvas.getContext('2d');

        let img = new Image()
        let imgUrl = null;

        img.onload = () => {
            ctx.drawImage(img, 0, 0);
            (URL || webkitURL).revokeObjectURL(imgUrl);
        }

        const show = function (jpeg) {
            let blob = new Blob([jpeg], {type: "image/jpeg"});
            imgUrl = (URL || webkitURL).createObjectURL(blob);
            img.src = imgUrl;
        }

        this.framesList = [];
        this.closed = false;

        let shiftFrame = () => {
            while(this.framesList.length > 3) this.framesList.shift();
            let frame = this.framesList.shift();
            if(frame) show(frame);

            if(!this.closed) requestAnimationFrame(shiftFrame);
        };


        shiftFrame();
    }

    on_frame(frame){
        this.framesList.push(frame);
    }

    close(){
        this.closed = true;
    }
};

