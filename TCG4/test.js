class GameComponent {
    constructor(data = {}) {
        Object.assign(this, data)
        this._uicomponent = null
    }

    makeUiComponent() {
        if (this._uicomponent) {
            delete this._uicomponent;
        }
        this._uicomponent = document.createElement('div');
        return this.getUiComponent();
    }

    getUiComponent() {
        if (this._uicomponent instanceof HTMLDivElement) {
            return this._uicomponent;
        } else {
            return null;
        }
    }
}

class Board {
    constructor() {
        this.player1 = GameComponent();
        this.player2 = GameComponent();
        this.players = [this.player1, this.player2];
        
        this.bottomrow = {};
        this.upperrow = {};
        for (player in this.players) {
            this.bottomrow[this.player] = GameComponent();
            this.upperrow[this.player] = GameComponent();
            this.deck[this.player] = GameComponent();
        }
    }
}