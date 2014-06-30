var canvas = document.createElement('canvas');
if (canvas.getContext && canvas.getContext('2d')) {
    var g = canvas.getContext('2d');
//    g.imageSmoothingEnabled = true;
    HTMLImageElement.prototype.resize = function(width, height) {
        canvas.width = width;
        canvas.height = height;
        g.drawImage(this, 0, 0, width, height);
        this.src = /\.png|\.gif$/.test(this.src)
            ? canvas.toDataURL('image/png') : canvas.toDataURL('image/jpeg', 0.75);
    };

    HTMLImageElement.prototype.setMaxSize = function(width, height) {
        if (this.width < width && this.height < height)
            return;
        if (!this.height || !this.width)
            console.error('Invalid image ' + this.src);
        var ratio = this.width / this.height;
        var ratio_max = width / height;
        if (ratio_max < ratio)
            this.resize(width, width / ratio);
        else
            this.resize(height * ratio, height);
    };
}
else
    console.error('Canvas is not supported');