class GameComponent {
    constructor(data = {}) {
        Object.assign(this, data)
        this._element = null
    }
}

class StaticComponent extends GameComponent {
    /**  @param {string} id */
    constructor(id, data = {}) {
        super(data);
        elem = document.getElementById(id);
        if (elem) {
            this._element = elem;
        } else {
            throw Error('StaticComponent element not pre-existing!');
        }
    }
}

class Board {
    constructor() {
        this.player1 = GameComponent();
        this.player2 = GameComponent();
        this.players = [this.player1, this.player2];
        
        this.bottomrow = StaticComponent("bottomrow1");
        this.upperrow = StaticComponent("upperrow1");
        for (player in this.players) {
            this.bottomrow[this.player] = GameComponent();
            this.upperrow[this.player] = GameComponent();
            this.deck[this.player] = GameComponent();
        }
    }

    init() {
        this.boardElement = document.getElementById('board');
    }

    render() {
        
    }
}

board = new Board();
board.init();