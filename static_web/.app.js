'use strict';
class App {
    constructor() {
        console.log("App start");
        this._el_list_path = document.getElementById("list-path");
        this._el_list = document.getElementById("list");
        this._el_app = document.getElementById("app");
        this._el_title = document.getElementById("title");
        this._el_search = document.getElementById("search");
        this._el_search.addEventListener("input", ev => this.show())
        document.addEventListener('keydown', (event) => {
            if (!event.ctrlKey &&
                !event.shiftKey &&
                !event.altKey &&
                !event.metaKey &&
                event.keyCode > 64 && event.keyCode < 91) {
                this._el_search.focus();
                return;
            }
            switch (event.key) {
                case "Escape":
                    // because firefox is broken
                    setTimeout(function(){
                        this._el_search.value = "";
                        this.show();
                    }.bind(this), 16);
                    break;
                case "Enter":
                case "Tab":
                    break;
                default:
                    break;
            }
        });

        this.path = this._el_list_path.innerText.trim()
        console.log("current path:", this.path);

        this.show();
    }

    show() {
        let search_term = this._el_search.value.toLowerCase();
        this.parseList(search_term);

        if (this.path === "/"){
            this.mode = "home";
            this.setTitle("");
            this.showHome();
        } else if (this.path.startsWith("/Filmid")){
            this.mode = "movies";
            this.setTitle(this.path);
            this.showFolder();
        } else {
            this.mode = "folder";
            this.setTitle(this.path);
            this.showFolder();
        }
    }

    parseList(search_term) {
        let ls = document.getElementById("list").querySelectorAll("tbody a");
        if (search_term) {
            this.list = Array.prototype.slice.call(ls).filter(el => el.title.toLowerCase().includes(search_term));
        } else {
            this.list = Array.prototype.slice.call(ls);
        }
    }

    setTitle(title) {
        document.title = title;
        this._el_title.innerHTML = `<a href="/">media.arti.ee</a>${title}`;
    }

    showHome() {
        let app = ""
        for (let el of this.list) {
            let href = el.getAttribute("href");
            if (href === 'favicon.ico') {
                continue;
            }
            if (el.title === 'd') {
                href += '?C=M&O=D';
            }
            app += `<div style="text-align: center; display: inline-block;"><a href="${href}">`
            switch (el.title) {
                case "d":
                case "d2":
                app += `
                    <svg style="display: block;" fill="#FFFFFF" height="250" viewBox="0 0 24 24" width="250" xmlns="http://www.w3.org/2000/svg">
                        <path d="M19.35 10.04C18.67 6.59 15.64 4 12 4 9.11 4 6.6 5.64 5.35 8.04 2.34 8.36 0 10.91 0 14c0 3.31 2.69 6 6 6h13c2.76 0 5-2.24 5-5 0-2.64-2.05-4.78-4.65-4.96zM17 13l-5 5-5-5h3V9h4v4h3z"/>
                    </svg>
                `;
                break;
                case "Filmid":
                app += `
                    <svg style="display: block;" fill="#FFFFFF" height="250" viewBox="0 0 24 24" width="250" xmlns="http://www.w3.org/2000/svg">
                        <path d="M18 3v2h-2V3H8v2H6V3H4v18h2v-2h2v2h8v-2h2v2h2V3h-2zM8 17H6v-2h2v2zm0-4H6v-2h2v2zm0-4H6V7h2v2zm10 8h-2v-2h2v2zm0-4h-2v-2h2v2zm0-4h-2V7h2v2z"/>
                    </svg>
                `;
                break;
                case "Seriaalid":
                app += `
                    <svg style="display: block;" fill="#FFFFFF" height="250" viewBox="0 0 24 24" width="250" xmlns="http://www.w3.org/2000/svg">
                        <path d="M21 6h-7.59l3.29-3.29L16 2l-4 4-4-4-.71.71L10.59 6H3c-1.1 0-2 .89-2 2v12c0 1.1.9 2 2 2h18c1.1 0 2-.9 2-2V8c0-1.11-.9-2-2-2zm0 14H3V8h18v12zM9 10v8l7-4z"/>
                    </svg>
                `;
                break;
                default:
                app += `
                    <svg style="display: block;" fill="#FFFFFF" height="250" viewBox="0 0 24 24" width="250" xmlns="http://www.w3.org/2000/svg">
                        <path d="M10 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V8c0-1.1-.9-2-2-2h-8l-2-2z"/>
                    </svg>
                `
            }
            app += `<span>${el.title}</span></a></div>`
        }
        this._el_app.innerHTML = app;
        this._el_app.classList.add("home");
    }

    showFolder() {
        //this._el_list.style.display = "block";
        let app = ``
        for (let el of this.list) {
            let href = el.getAttribute("href").split("?")[0]
            app += `<div class="folder-line"><a href="${href}"> `
            if (href.endsWith("/")) {
                app += `
                    <svg fill="#FFFFFF" height="24" viewBox="0 0 24 24" width="24" xmlns="http://www.w3.org/2000/svg">
                        <path d="M10 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V8c0-1.1-.9-2-2-2h-8l-2-2z"/>
                    </svg>
                `
            } else {
                app += `
                    <svg fill="#FFFFFF" height="24" viewBox="0 0 24 24" width="24" xmlns="http://www.w3.org/2000/svg">
                        <path d="M6 2c-1.1 0-1.99.9-1.99 2L4 20c0 1.1.89 2 1.99 2H18c1.1 0 2-.9 2-2V8l-6-6H6zm7 7V3.5L18.5 9H13z"/>
                    </svg>
                `
            }


            app +=`${el.innerText}</a></div>`
        }
        this._el_app.innerHTML = app;
    }
}
