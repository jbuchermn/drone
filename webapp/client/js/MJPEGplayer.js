export default class MJPEGplayer{
    constructor(canvas, {
        x, y, w, h, flipped
    }) {
        let ctx = canvas.getContext('2d');
        if(!ctx){
            console.log("Unable to open canvas");
            return;
        }

        if(flipped) ctx.scale(-1, -1);

        let img = new Image()
        let imgUrl = null;

        img.onload = () => {
            if(flipped) ctx.drawImage(img, -x, -y, -w, -h);
                else ctx.drawImage(img, x, y, w, h);
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

