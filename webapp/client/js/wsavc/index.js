var YUVWebGLCanvas = require('./canvas/YUVWebGLCanvas');
var YUVCanvas = require('./canvas/YUVCanvas');
var Size = require('./utils/Size');

// Requires lib/broadway/Decoder.js defining global Decoder

export default class Wsavc{
    constructor(canvas, {
        type,
        width,
        height
    }) {
        if(!width) throw "Need to supply width";
        if(!height) throw "Need to supply height";

        type = type || "webgl";

        canvas.width  = width;
        canvas.height = height;

        let canvasFactory = type == "webgl" ? YUVWebGLCanvas : YUVCanvas;
        let yuv = new canvasFactory(canvas, new Size(width, height));

        let decoder = new Decoder();
        decoder.onPictureDecoded = yuv.decode;

        this.framesList = [];
        this.closed = false;

        let shiftFrame = () => {
            if(this.framesList.length > 10) this.framesList = [];
            let frame = this.framesList.shift();
            if(frame) decoder.decode(frame);

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

