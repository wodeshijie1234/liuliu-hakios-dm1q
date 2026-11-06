/* SPDX-License-Identifier: MIT
 * Copyright (c) 2026 liuliu
 * UEFI console probe only: no partitions, persistent variables, or MMIO writes.
 * Requires a separately validated UEFI environment. Not an Android boot image.
 */
#include "efi.h"

static efi_system_table *system_table;

static void say(const char16 *text)
{
    system_table->con_out->output_string(system_table->con_out, text);
}

static void hex(uint64_t value)
{
    static const char16 digits[] = u"0123456789abcdef";
    char16 text[19] = { '0', 'x' };
    for (unsigned i = 0; i < 16; ++i)
        text[i + 2] = digits[(value >> ((15 - i) * 4)) & 15];
    say(text);
}

static void field(const char16 *name, uint64_t value)
{
    say(name);
    hex(value);
    say(u"\r\n");
}

efi_status EFIAPI EfiMain(efi_handle image, efi_system_table *table)
{
    (void)image;
    if (!table || !table->con_out || !table->con_out->output_string || !table->bs)
        return EFI_ERROR_BIT | 3; /* EFI_UNSUPPORTED */
    system_table = table;
    say(u"liuliu dm1q UEFI probe 0.1.0-dev\r\n");
    say(u"No XNU loaded. Device identity NOT validated by this program.\r\n");
    uint64_t el, midr, frequency;
    __asm__ volatile("mrs %0, CurrentEL" : "=r"(el));
    __asm__ volatile("mrs %0, MIDR_EL1" : "=r"(midr));
    __asm__ volatile("mrs %0, CNTFRQ_EL0" : "=r"(frequency));
    field(u"CurrentEL: ", el >> 2);
    field(u"MIDR_EL1: ", midr);
    field(u"CNTFRQ_EL0: ", frequency);
    field(u"UEFI revision: ", table->hdr.revision);

    static const efi_guid gop_guid = EFI_GOP_GUID;
    efi_gop *gop = NULL;
    efi_status status = table->bs->locate_protocol(&gop_guid, NULL, (void **)&gop);
    if (!EFI_ERROR(status) && gop && gop->mode && gop->mode->info) {
        field(u"Framebuffer base: ", gop->mode->fb_base);
        field(u"Framebuffer bytes: ", gop->mode->fb_size);
        field(u"Width: ", gop->mode->info->width);
        field(u"Height: ", gop->mode->info->height);
        field(u"Pixels per scanline: ", gop->mode->info->pixels_per_scanline);
        field(u"Pixel format: ", gop->mode->info->pixel_format);
    } else {
        field(u"No GOP; status: ", status);
    }

    /* No allocation or ExitBootServices: inspect a fixed-size snapshot only. */
    static uint64_t memory_map[16384];
    uint64_t map_size = sizeof(memory_map), map_key = 0, descriptor_size = 0;
    uint32_t descriptor_version = 0;
    status = table->bs->get_memory_map(&map_size, memory_map, &map_key,
                                      &descriptor_size, &descriptor_version);
    field(u"GetMemoryMap status: ", status);
    if (!EFI_ERROR(status) && descriptor_size >= sizeof(efi_memory_descriptor)
        && map_size >= descriptor_size && map_size <= sizeof(memory_map)) {
        field(u"Memory descriptors: ", map_size / descriptor_size);
        for (uint64_t offset = 0; offset <= map_size - descriptor_size;
             offset += descriptor_size) {
            efi_memory_descriptor *entry = (void *)((uint8_t *)memory_map + offset);
            say(u"type/base/pages/attributes: ");
            hex(entry->type); say(u" ");
            hex(entry->phys_start); say(u" ");
            hex(entry->pages); say(u" ");
            hex(entry->attribute); say(u"\r\n");
        }
    }
    say(u"Probe finished. Returning to the UEFI caller; no reset requested.\r\n");
    table->bs->stall(5000000);
    return 0;
}
