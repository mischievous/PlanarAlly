<script lang="ts">
import Vue from "vue";
import Component from "vue-class-component";

import Modal from "@/core/components/modals/modal.vue";
import { uuidv4 } from "@/core/utils";
import { socket } from "@/game/api/socket";
import { gameStore } from "@/game/store";

import { Label } from "../shapes/interfaces";

@Component({
    components: {
        Modal,
    },
})
export default class LabelManager extends Vue {
    visible = false;
    newCategory = "";
    newName = "";
    search = "";

    open(): void {
        this.visible = true;
        this.newCategory = "";
        this.newName = "";
        this.$nextTick(() => (this.$refs.search as HTMLInputElement).focus());
    }

    get labels(): { [category: string]: Label[] } {
        const cat: { [category: string]: Label[] } = { "": [] };
        for (const uuid of Object.keys(gameStore.labels)) {
            const label = gameStore.labels[uuid];
            if (
                this.search.length &&
                `${label.category.toLowerCase()}${label.name.toLowerCase()}`.search(this.search.toLowerCase()) < 0
            )
                continue;
            if (label.user !== gameStore.username) continue;
            if (!label.category) cat[""].push(label);
            else {
                if (!(label.category in cat)) cat[label.category] = [];
                cat[label.category].push(label);
                cat[label.category].sort((a, b) => a.name.localeCompare(b.name));
            }
        }
        return cat;
    }

    get categories(): string[] {
        return Object.keys(this.labels).sort();
    }

    selectLabel(label: string): void {
        this.$emit("addLabel", label);
        this.visible = false;
    }

    toggleVisibility(label: Label): void {
        label.visible = !label.visible;
        socket.emit("Label.Visibility.Set", { uuid: label.uuid, visible: label.visible });
    }

    addLabel(): void {
        if (this.newName === "") return;
        const label = {
            uuid: uuidv4(),
            category: this.newCategory,
            name: this.newName,
            visible: false,
            user: gameStore.username,
        };
        gameStore.addLabel(label);
        socket.emit("Label.Add", label);
        this.newCategory = "";
        this.newName = "";
    }

    deleteLabel(uuid: string): void {
        gameStore.deleteLabel({ uuid, user: gameStore.username });
        socket.emit("Label.Delete", uuid);
    }
}
</script>

<template>
    <Modal :visible="visible" @close="visible = false" :mask="false">
        <div
            class="modal-header"
            slot="header"
            slot-scope="m"
            draggable="true"
            @dragstart="m.dragStart"
            @dragend="m.dragEnd"
        >
            <div v-t="'game.ui.labels.title'"></div>
            <div class="header-close" @click="visible = false" :title="$t('common.close')">
                <font-awesome-icon :icon="['far', 'window-close']" />
            </div>
        </div>
        <div class="modal-body">
            <div class="grid">
                <div>
                    <abbr :title="$t('game.ui.labels.category')" v-t="'game.ui.labels.cat_abbr'"></abbr>
                </div>
                <div class="name" v-t="'common.name'"></div>
                <div>
                    <abbr :title="$t('game.ui.labels.visible')" v-t="'game.ui.labels.vis_abbr'"></abbr>
                </div>
                <div>
                    <abbr :title="$t('game.ui.labels.delete')" v-t="'game.ui.labels.del_abbr'"></abbr>
                </div>
                <div class="separator spanrow" style="margin: 0 0 7px"></div>
                <input class="spanrow" type="text" :placeholder="$t('common.search')" v-model="search" ref="search" />
            </div>
            <div class="grid scroll">
                <template v-for="category in categories">
                    <template v-for="label in labels[category]">
                        <div :key="'row-' + label.uuid" class="row" @click="selectLabel(label.uuid)">
                            <template v-if="label.category">
                                <div :key="'cat-' + label.uuid">{{ label.category }}</div>
                                <div class="name" :key="'name-' + label.uuid">{{ label.name }}</div>
                            </template>
                            <template v-if="!label.category">
                                <div :key="'cat-' + label.uuid"></div>
                                <div class="name" :key="'name-' + label.uuid">{{ label.name }}</div>
                            </template>
                            <div
                                :key="'visible-' + label.uuid"
                                :style="{ textAlign: 'center' }"
                                :class="{ 'lower-opacity': !label.visible }"
                                @click.stop="toggleVisibility(label)"
                                :title="$t('common.toggle_public_private')"
                            >
                                <font-awesome-icon icon="eye" />
                            </div>
                            <div
                                :key="'delete-' + label.uuid"
                                @click.stop="deleteLabel(label.uuid)"
                                :title="$t('game.ui.labels.delete_label')"
                            >
                                <font-awesome-icon icon="trash-alt" />
                            </div>
                        </div>
                    </template>
                </template>
                <template v-if="Object.keys(labels).length === 0">
                    <div id="no-labels" v-t="'game.ui.labels.no_exist_msg'"></div>
                </template>
            </div>
            <div class="grid">
                <div class="separator spanrow"></div>
                <input type="text" v-model.trim="newCategory" />
                <input type="text" v-model.trim="newName" />
                <button id="addLabelButton" @click.stop="addLabel" v-t="'common.add'"></button>
            </div>
        </div>
    </Modal>
</template>

<style scoped lang="scss">
abbr {
    text-decoration: none;
}

.scroll {
    max-height: 20em;
    overflow-y: auto;
}

.modal-header {
    background-color: #ff7052;
    padding: 10px;
    font-size: 20px;
    font-weight: bold;
    cursor: move;
}

.header-close {
    position: absolute;
    top: 5px;
    right: 5px;
}

.modal-body {
    padding: 10px;
    max-width: 450px;
}

.separator {
    line-height: 0.1em;
    margin: 7px 0;

    &:after {
        position: absolute;
        left: 10px;
        right: 10px;
        border-bottom: 1px solid #000;
        content: "";
    }
}

.spanrow {
    grid-column: start / end;
}

.lower-opacity > * {
    opacity: 0.3;
}

.grid {
    display: grid;
    grid-template-columns: [start] 50px [name] 1fr [visible] 30px [remove] 30px [end];
    grid-row-gap: 5px;
    align-items: center;

    > * {
        text-align: center;
    }
}

.name {
    text-align: left !important;
}

.row {
    display: contents;

    > * {
        padding: 5px;
        height: 20px;
        border: solid 1px rgba(0, 0, 0, 0);
    }

    &:hover > * {
        cursor: pointer;
        border-top: solid 1px #ff7052;
        border-bottom: solid 1px #ff7052;
        background-color: rgba(0, 0, 0, 0.2);

        &:first-child {
            border-left: solid 1px #ff7052;
            border-top-left-radius: 10px;
            border-bottom-left-radius: 10px;
        }

        &:last-child {
            border-right: solid 1px #ff7052;
            border-top-right-radius: 10px;
            border-bottom-right-radius: 10px;
        }
    }
}

#no-labels {
    grid-column: start/end;
    font-style: italic;
    padding-left: 50px;
}

#addLabelButton {
    grid-column: visible/end;
}
</style>
