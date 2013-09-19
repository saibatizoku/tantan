$(document).ready(function() {

    var cats = new AngryCats([
            new AngryCat({ name: 'Wet Cat', image_path: 'assets/images/cat2.jpg' }),
            new AngryCat({ name: 'Bitey Cat', image_path: 'assets/images/cat1.jpg' }),
            new AngryCat({ name: 'Surprised Cat', image_path: 'assets/images/cat3.jpg' })
            ]);

    MyApp.start({cats: cats});

    cats.add(new AngryCat({
        name: 'Cranky Cat',
        image_path: 'assets/images/cat4.jpg',
        rank: cats.size() + 1
    }));
});
